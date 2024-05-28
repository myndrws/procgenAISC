#include "../basic-abstract-game.h"
#include "../assetgen.h"
#include <cstdlib>
#include <set>
#include <queue>

const std::string NAME = "treechop";

const int TREE_REWARD = 1.0;
const int MAX_TREES = 3;
const double R_MIN = 0.000001;
const double R_MAX = 0.3;
const double N_MAX = 10;

// TODO
// checkout the rewarding and counting of trees remaining
// tree appearance during the game

const int TREE = 10;
const int TREESTUMP = 0;

class TreeChop : public BasicAbstractGame {
  public:
    int trees_chopped = 0;

    TreeChop()
        : BasicAbstractGame(NAME) {
        timeout = 6400; // number of steps to timeout after

        main_width = 20;
        main_height = 20;

        mixrate = .5;
        maxspeed = .5;
        has_useful_vel_info = false;

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
            step_data.reward += TREE_REWARD;
            obj->will_erase = true;
            trees_chopped += 1;
      }

         // will need another condition at some point to end the game
         // with step_data.done = true;
         // if reached a certain amount of reward and trees chopped

    }

    bool is_free(int idx) {
        return get_obj(idx) == SPACE && (get_agent_index() != idx);
    }

    int get_agent_index() {
        return int(agent->y) * main_width + int(agent->x);
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

        trees_chopped = 0;

        int main_area = main_height * main_width;

        options.center_agent = options.distribution_mode == MemoryMode;
        grid_step = true;

        std::vector<int> obj_idxs = rand_gen.simple_choose(main_area, MAX_TREES + 1);

        int agent_x = obj_idxs[0] % main_width;
        int agent_y = obj_idxs[0] / main_width;

        agent->x = agent_x + .5;
        agent->y = agent_y + .5;

        for (int i = 0; i < MAX_TREES; i++) {
            int cell = obj_idxs[i + 1];
            set_obj(cell, TREE);
        }

        set_obj(int(agent->x), int(agent->y), SPACE);

    }

    void set_action_xy(int move_action) override {
        BasicAbstractGame::set_action_xy(move_action);
        if (action_vx != 0)
            action_vy = 0;
    }

    void game_step() override {
        BasicAbstractGame::game_step();

        if (action_vx > 0)
            agent->is_reflected = false;
        if (action_vx < 0)
            agent->is_reflected = true;

        int ix = int(agent->x);
        int iy = int(agent->y);
        if (get_obj(ix, iy) == TREE) {
            set_obj(ix, iy, SPACE);
            step_data.reward += TREE_REWARD;
        }

        int main_area = main_width * main_height;
        int trees_count = 0;

        // count trees
        for (int idx = 0; idx < main_area; idx++){
            if (get_obj(idx) == TREE) {
                trees_count++;
            }
        }

        // probability of a new tree spawning at a random empty location
        double respawn_prob = std::max(R_MIN, R_MAX * std::log(1.0 + trees_count) / std::log(1.0 + MAX_TREES));

        // respawn a new tree
        // per episode step
        // place a new tree with respawn probability
        // if there are fewer than the max trees
        // sample 1 from the grid where == SPACE only
        // then place a tree
        if (trees_count < MAX_TREES) {

            if (rand_gen.rand01() < respawn_prob) {

            // get the free space on the grid
            std::vector<int> free_indexes;
            for (int i = 0; i < main_area; ++i) {
                if (is_free(i)) {
                    free_indexes.push_back(i);
                }
            }

            // select one of those free spaces for a tree
            int random_idx = rand() % free_indexes.size();
            set_obj(random_idx, TREE);

            }

        }

    }

    void serialize(WriteBuffer *b) override {
        BasicAbstractGame::serialize(b);
        b->write_int(trees_chopped);
    }

    void deserialize(ReadBuffer *b) override {
        BasicAbstractGame::deserialize(b);
        trees_chopped = b->read_int();
    }
};

REGISTER_GAME(NAME, TreeChop);
