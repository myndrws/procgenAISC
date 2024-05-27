#include "../basic-abstract-game.h"
#include "../assetgen.h"
#include <set>
#include <queue>

const std::string NAME = "treechop";

const float COMPLETION_BONUS = 10.0;
const int TREE_REWARD = 1.0;

// TODO
// get rid of the jumpi-ness by testing removing the SPACE thing
// make trees disappear on collision to be replaced by treestumps ideally
// checkout the rewarding and counting of trees remaining

const int TREE = 10;
const int TREESTUMP = 0;
const int TREES_CHOPPED = 0;

const int OOB_WALL = 10;

class TreeChop : public BasicAbstractGame {
  public:
    int trees_remaining = 0;

    TreeChop()
        : BasicAbstractGame(NAME) {
        main_width = 20;
        main_height = 20;

        mixrate = .5;
        maxspeed = .5;
        has_useful_vel_info = false;

        out_of_bounds_object = OOB_WALL;
        visibility = 8.0;
    }

    void load_background_images() override {
        main_bg_images_ptr = &forest_background;
    }

    void asset_for_type(int type, std::vector<std::string> &names) override {
        if (type == PLAYER) {
            names.push_back("misc_assets/tree_chopper.png");
        } else if (type == TREE) {
            names.push_back("misc_assets/tree.png");
        } else if (type == TREESTUMP) {
            names.push_back("misc_assets/tree_stump.png");
        }
    }

    void handle_agent_collision(const std::shared_ptr<Entity> &obj) override {
        BasicAbstractGame::handle_agent_collision(obj);

        if (obj->type == TREE) {
            if (obj->rx > agent->rx) {
                step_data.reward += TREE_REWARD;
                obj->will_erase = true;
            }

      }

         // will need another condition at some point to end the game
         // with step_data.done = true;
         // if reached a certain amount of reward and trees chopped

    }

    int get_agent_index() {
        return int(agent->y) * main_width + int(agent->x);
    }

    void set_action_xy(int move_action) override {
        BasicAbstractGame::set_action_xy(move_action);
        if (action_vx != 0)
            action_vy = 0;
    }

    void choose_world_dim() override {
        int dist_diff = options.distribution_mode;

        if (dist_diff == EasyMode) {
            main_width = 10;
            main_height = 10;
        } else if (dist_diff == HardMode) {
            main_width = 20;
            main_height = 20;
        } else if (dist_diff == MemoryMode) {
            main_width = 35;
            main_height = 35;
        }
    }

    void game_reset() override {
        BasicAbstractGame::game_reset();

        agent->rx = .5;
        agent->ry = .5;

        int main_area = main_height * main_width;

        options.center_agent = options.distribution_mode == MemoryMode;
        grid_step = true;

        float tree_pct = 12 / 400.0f;

        int num_trees = (int)(tree_pct * grid_size);

        std::vector<int> obj_idxs = rand_gen.simple_choose(main_area, num_trees + 1);

        int agent_x = obj_idxs[0] % main_width;
        int agent_y = obj_idxs[0] / main_width;

        agent->x = agent_x + .5;
        agent->y = agent_y + .5;

        for (int i = 0; i < num_trees; i++) {
            int cell = obj_idxs[i + 1];
            set_obj(cell, TREE);
        }

        set_obj(int(agent->x), int(agent->y), SPACE);

    }

    bool is_free(int idx) {
        return get_obj(idx) == SPACE && (get_agent_index() != idx);
    }

    void game_step() override {
        BasicAbstractGame::game_step();

        if (action_vx > 0)
            agent->is_reflected = false;
        if (action_vx < 0)
            agent->is_reflected = true;

        int agent_obj = get_obj(int(agent->x), int(agent->y));

        if (agent_obj == TREE) {
            set_obj(int(agent->x), int(agent->y), SPACE);
            step_data.reward += TREE_REWARD;
        }

        int main_area = main_width * main_height;

        int tree_count = 0;

        for (int idx = 0; idx < main_area; idx++) {
            int obj = get_obj(idx);
            int obj_x = idx % main_width;
            int agent_idx = (agent->y - .5) * main_width + (agent->x - .5);
            if (obj == TREE) {
                tree_count++;
            }

        trees_remaining = tree_count;

        }
    }

    void serialize(WriteBuffer *b) override {
        BasicAbstractGame::serialize(b);
        b->write_int(trees_remaining);
    }

    void deserialize(ReadBuffer *b) override {
        BasicAbstractGame::deserialize(b);
        trees_remaining = b->read_int();
    }
};

REGISTER_GAME(NAME, TreeChop);
