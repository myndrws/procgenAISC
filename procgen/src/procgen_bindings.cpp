#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "vecgame.h"
#include "vecoptions.h"
#include "libenv.h"
#include <cstring>
#include <iostream>

namespace py = pybind11;

// Forward declarations for state management functions
extern "C" {
    int get_state(libenv_env *handle, int env_idx, char *data, int length);
    void set_state(libenv_env *handle, int env_idx, char *data, int length);
}

class ProcgenVecEnv {
private:
    VecGame* vec_game;
    int num_envs;

    // Storage for options data - must persist for lifetime of VecGame
    std::vector<std::string> option_name_storage;
    std::vector<std::vector<char>> option_data_storage;

    // Numpy arrays for buffers
    py::array_t<uint8_t> obs_array;
    py::array_t<int32_t> action_array;
    py::array_t<float> reward_array;
    py::array_t<uint8_t> first_array;

    // Info buffers - dynamically allocated based on info_types
    std::vector<py::array_t<uint8_t>> info_uint8_arrays;
    std::vector<py::array_t<int32_t>> info_int32_arrays;
    std::vector<std::string> info_uint8_names;
    std::vector<std::string> info_int32_names;

public:
    ProcgenVecEnv(int num_envs, const std::map<std::string, py::object>& options) {
        std::cout << "[DEBUG] ProcgenVecEnv::__init__ starting, num_envs=" << num_envs << std::endl;
        this->num_envs = num_envs;

        // Convert Python options to C++ libenv_options
        std::cout << "[DEBUG] Converting options to C++ structures..." << std::endl;
        std::vector<libenv_option> option_items;

        for (const auto& [key, value] : options) {
            std::cout << "[DEBUG]   Processing option: " << key << std::endl;
            libenv_option opt;
            option_name_storage.push_back(key);
            opt.name = option_name_storage.back().c_str();

            if (py::isinstance<py::bool_>(value)) {
                opt.dtype = LIBENV_DTYPE_UINT8;
                opt.count = 1;
                option_data_storage.push_back(std::vector<char>(1));
                option_data_storage.back()[0] = value.cast<bool>() ? 1 : 0;
                opt.data = option_data_storage.back().data();
            } else if (py::isinstance<py::int_>(value)) {
                opt.dtype = LIBENV_DTYPE_INT32;
                opt.count = 1;
                option_data_storage.push_back(std::vector<char>(sizeof(int32_t)));
                *reinterpret_cast<int32_t*>(option_data_storage.back().data()) = value.cast<int32_t>();
                opt.data = option_data_storage.back().data();
            } else if (py::isinstance<py::str>(value)) {
                std::string str_val = value.cast<std::string>();
                opt.dtype = LIBENV_DTYPE_UINT8;
                opt.count = str_val.size();
                option_data_storage.push_back(std::vector<char>(str_val.begin(), str_val.end()));
                opt.data = option_data_storage.back().data();
            } else {
                throw std::runtime_error("Unsupported option type for key: " + key);
            }

            option_items.push_back(opt);
        }

        std::cout << "[DEBUG] Creating libenv_options with " << option_items.size() << " options" << std::endl;
        libenv_options c_options;
        c_options.count = option_items.size();
        c_options.items = option_items.data();

        std::cout << "[DEBUG] Creating VecOptions from c_options..." << std::endl;
        VecOptions vec_opts(c_options);

        std::cout << "[DEBUG] Creating VecGame..." << std::endl;
        vec_game = new VecGame(num_envs, vec_opts);
        std::cout << "[DEBUG] VecGame created successfully!" << std::endl;

        std::cout << "[DEBUG] Allocating numpy buffers..." << std::endl;
        // Allocate numpy arrays
        allocate_buffers();
        std::cout << "[DEBUG] Setting up C++ buffer pointers..." << std::endl;
        setup_cpp_buffers();
        std::cout << "[DEBUG] ProcgenVecEnv::__init__ complete!" << std::endl;
    }

    ~ProcgenVecEnv() {
        std::cout << "[DEBUG] ProcgenVecEnv::~ProcgenVecEnv() starting..." << std::endl;
        std::cout.flush();
        if (vec_game) {
            std::cout << "[DEBUG] Deleting vec_game..." << std::endl;
            std::cout.flush();
            delete vec_game;
            std::cout << "[DEBUG] vec_game deleted successfully" << std::endl;
            std::cout.flush();
        }
        std::cout << "[DEBUG] ProcgenVecEnv::~ProcgenVecEnv() complete" << std::endl;
        std::cout.flush();
    }

    void allocate_buffers() {
        std::cout << "[DEBUG allocate_buffers] Starting..." << std::endl;
        std::cout.flush();
        std::cout << "[DEBUG allocate_buffers] Allocating obs array: (" << num_envs << ", 64, 64, 3)" << std::endl;
        std::cout.flush();
        // Observation buffer: (num_envs, 64, 64, 3)
        obs_array = py::array_t<uint8_t>({num_envs, 64, 64, 3});
        std::cout << "[DEBUG allocate_buffers] obs_array allocated successfully" << std::endl;
        std::cout.flush();

        // Action buffer: (num_envs,)
        action_array = py::array_t<int32_t>(num_envs);

        // Reward buffer: (num_envs,)
        reward_array = py::array_t<float>(num_envs);

        // First/done buffer: (num_envs,)
        first_array = py::array_t<uint8_t>(num_envs);

        std::cout << "[DEBUG allocate_buffers] Processing " << vec_game->info_types.size() << " info types..." << std::endl;
        std::cout.flush();
        // Info buffers based on vec_game->info_types
        for (const auto& t : vec_game->info_types) {
            std::string name(t.name);
            std::cout << "[DEBUG allocate_buffers]   Info type: " << name << ", dtype=" << t.dtype << ", ndim=" << t.ndim << std::endl;
            std::cout.flush();

            if (t.dtype == LIBENV_DTYPE_UINT8) {
                if (t.ndim == 3) {
                    // RGB render buffer (RENDER_RES x RENDER_RES x 3)
                    std::cout << "[DEBUG allocate_buffers]     Allocating RGB buffer: (" << num_envs << ", " << t.shape[0] << ", " << t.shape[1] << ", " << t.shape[2] << ")" << std::endl;
                    info_uint8_arrays.push_back(
                        py::array_t<uint8_t>({num_envs, t.shape[0], t.shape[1], t.shape[2]})
                    );
                } else {
                    // Scalar info
                    std::cout << "[DEBUG allocate_buffers]     Allocating scalar buffer: (" << num_envs << ")" << std::endl;
                    info_uint8_arrays.push_back(py::array_t<uint8_t>(num_envs));
                }
                info_uint8_names.push_back(name);
            } else if (t.dtype == LIBENV_DTYPE_INT32) {
                // Scalar info
                std::cout << "[DEBUG allocate_buffers]     Allocating int32 buffer: (" << num_envs << ")" << std::endl;
                info_int32_arrays.push_back(py::array_t<int32_t>(num_envs));
                info_int32_names.push_back(name);
            }
        }
        std::cout << "[DEBUG allocate_buffers] Complete!" << std::endl;
    }

    void setup_cpp_buffers() {
        std::vector<std::vector<void*>> ac(num_envs);
        std::vector<std::vector<void*>> ob(num_envs);
        std::vector<std::vector<void*>> info(num_envs);

        auto obs_ptr = obs_array.mutable_data();
        auto action_ptr = action_array.mutable_data();

        for (int i = 0; i < num_envs; i++) {
            // Action pointers (one action per env)
            ac[i].resize(1);
            ac[i][0] = &action_ptr[i];

            // Observation pointers (one RGB observation per env)
            ob[i].resize(1);
            ob[i][0] = &obs_ptr[i * 64 * 64 * 3];

            // Info pointers
            info[i].resize(vec_game->info_types.size());
            size_t uint8_idx = 0, int32_idx = 0;

            for (size_t j = 0; j < vec_game->info_types.size(); j++) {
                const auto& t = vec_game->info_types[j];

                if (t.dtype == LIBENV_DTYPE_UINT8) {
                    auto& arr = info_uint8_arrays[uint8_idx];
                    auto ptr = arr.mutable_data();

                    if (t.ndim == 3) {
                        // RGB buffer: point to start of this env's data
                        int stride = t.shape[0] * t.shape[1] * t.shape[2];
                        info[i][j] = &ptr[i * stride];
                    } else {
                        // Scalar: point to this env's element
                        info[i][j] = &ptr[i];
                    }
                    uint8_idx++;
                } else if (t.dtype == LIBENV_DTYPE_INT32) {
                    auto& arr = info_int32_arrays[int32_idx];
                    auto ptr = arr.mutable_data();
                    info[i][j] = &ptr[i];
                    int32_idx++;
                }
            }
        }

        // Set buffers in VecGame
        vec_game->set_buffers(ac, ob, info,
                             reward_array.mutable_data(),
                             first_array.mutable_data());
    }

    void observe() {
        vec_game->observe();
    }

    void act() {
        vec_game->act();
    }

    py::array_t<uint8_t> get_obs() {
        return obs_array;
    }

    py::array_t<float> get_rewards() {
        return reward_array;
    }

    py::array_t<uint8_t> get_firsts() {
        return first_array;
    }

    py::dict get_info() {
        py::dict info_dict;

        // Add uint8 info
        for (size_t i = 0; i < info_uint8_arrays.size(); i++) {
            info_dict[info_uint8_names[i].c_str()] = info_uint8_arrays[i];
        }

        // Add int32 info
        for (size_t i = 0; i < info_int32_arrays.size(); i++) {
            info_dict[info_int32_names[i].c_str()] = info_int32_arrays[i];
        }

        return info_dict;
    }

    void set_action(py::array_t<int32_t> actions) {
        if (actions.size() != num_envs) {
            throw std::runtime_error("Action array size must match num_envs");
        }
        auto actions_ptr = actions.data();
        auto action_buf = action_array.mutable_data();
        std::memcpy(action_buf, actions_ptr, num_envs * sizeof(int32_t));
    }

    py::bytes get_state(int env_idx) {
        if (env_idx < 0 || env_idx >= num_envs) {
            throw std::runtime_error("env_idx out of range");
        }

        const int MAX_STATE_SIZE = 1 << 20;  // 2^20 bytes = 1MB
        std::vector<char> buffer(MAX_STATE_SIZE);

        int n = ::get_state(reinterpret_cast<libenv_env*>(vec_game), env_idx,
                           buffer.data(), MAX_STATE_SIZE);

        return py::bytes(buffer.data(), n);
    }

    void set_state(int env_idx, py::bytes state) {
        if (env_idx < 0 || env_idx >= num_envs) {
            throw std::runtime_error("env_idx out of range");
        }

        std::string state_str = state;
        ::set_state(reinterpret_cast<libenv_env*>(vec_game), env_idx,
                   const_cast<char*>(state_str.data()), state_str.size());
    }

    int get_num_envs() const {
        return num_envs;
    }
};

PYBIND11_MODULE(procgen_bindings, m) {
    m.doc() = "Procgen pybind11 bindings - direct C++ interface for Procgen environments";

    py::class_<ProcgenVecEnv>(m, "ProcgenVecEnv")
        .def(py::init<int, const std::map<std::string, py::object>&>(),
             py::arg("num_envs"),
             py::arg("options"),
             "Create a vectorized Procgen environment")
        .def("observe", &ProcgenVecEnv::observe,
             "Update observations from environments")
        .def("act", &ProcgenVecEnv::act,
             "Execute actions in environments")
        .def("get_obs", &ProcgenVecEnv::get_obs,
             "Get observation array (num_envs, 64, 64, 3)")
        .def("get_rewards", &ProcgenVecEnv::get_rewards,
             "Get reward array (num_envs,)")
        .def("get_firsts", &ProcgenVecEnv::get_firsts,
             "Get first/done flags (num_envs,)")
        .def("get_info", &ProcgenVecEnv::get_info,
             "Get info dictionary")
        .def("set_action", &ProcgenVecEnv::set_action,
             py::arg("actions"),
             "Set actions for all environments")
        .def("get_state", &ProcgenVecEnv::get_state,
             py::arg("env_idx"),
             "Get serialized state for environment")
        .def("set_state", &ProcgenVecEnv::set_state,
             py::arg("env_idx"),
             py::arg("state"),
             "Set serialized state for environment")
        .def("get_num_envs", &ProcgenVecEnv::get_num_envs,
             "Get number of parallel environments");
}
