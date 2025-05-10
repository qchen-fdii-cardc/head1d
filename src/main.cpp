#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>
#include <Eigen/Dense>
#include <iomanip>  // For std::fixed and std::setprecision
#include <getopt.h> // For command line argument parsing

// Function to print a vector to a stream for debugging or output
void printVector(const Eigen::VectorXd &vec, std::ostream &os = std::cout)
{
    for (int i = 0; i < vec.size(); ++i)
    {
        os << std::fixed << std::setprecision(6) << vec(i) << (i == vec.size() - 1 ? "" : ", ");
    }
    os << std::endl;
}

void printUsage(const char *programName)
{
    std::cerr << "Usage: " << programName << " [options] <num_cells>" << std::endl;
    std::cerr << "Options:" << std::endl;
    std::cerr << "  --alpha <value>     Thermal diffusivity (default: 0.01)" << std::endl;
    std::cerr << "  --dt <value>        Time step size (default: 0.01)" << std::endl;
    std::cerr << "  --time <value>      Total simulation time (default: 1.0)" << std::endl;
    std::cerr << "  --output <prefix>   Output file prefix (default: results/temperature)" << std::endl;
    std::cerr << "  --help              Display this help message" << std::endl;
}

int main(int argc, char *argv[])
{
    // Default parameter values
    double alpha = 0.01;     // Thermal diffusivity
    double dt = 0.01;        // Time step size
    double total_time = 1.0; // Total simulation time
    std::string output_prefix = "results/temperature";
    int num_x = -1;       // Number of spatial cells (must be provided)
    const double L = 1.0; // Fixed domain length

    // Define long options
    static struct option long_options[] = {
        {"alpha", required_argument, 0, 'a'},
        {"dt", required_argument, 0, 't'},
        {"time", required_argument, 0, 'T'},
        {"output", required_argument, 0, 'o'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}};

    // Parse command line options
    int opt;
    int option_index = 0;
    while ((opt = getopt_long(argc, argv, "a:t:T:o:h", long_options, &option_index)) != -1)
    {
        switch (opt)
        {
        case 'a':
            alpha = std::stod(optarg);
            break;
        case 't':
            dt = std::stod(optarg);
            break;
        case 'T':
            total_time = std::stod(optarg);
            break;
        case 'o':
            output_prefix = optarg;
            break;
        case 'h':
            printUsage(argv[0]);
            return 0;
        case '?':
            printUsage(argv[0]);
            return 1;
        default:
            abort();
        }
    }

    // Get the number of cells (required argument)
    if (optind < argc)
    {
        num_x = std::stoi(argv[optind]);
    }
    else
    {
        std::cerr << "Error: Number of cells is required." << std::endl;
        printUsage(argv[0]);
        return 1;
    }

    if (num_x <= 0)
    {
        std::cerr << "Error: Number of cells must be positive." << std::endl;
        return 1;
    }

    // Calculate dx based on fixed L and num_x
    double dx = L / (num_x + 1);
    int num_t_steps = static_cast<int>(total_time / dt);

    std::cout << "--- 1D Heat Conduction Simulation ---" << std::endl;
    std::cout << "Number of spatial cells (num_x): " << num_x << std::endl;
    std::cout << "Thermal diffusivity (alpha): " << alpha << std::endl;
    std::cout << "Spatial step (dx): " << dx << std::endl;
    std::cout << "Time step (dt): " << dt << std::endl;
    std::cout << "Total time: " << total_time << std::endl;
    std::cout << "Number of time steps: " << num_t_steps << std::endl;
    std::cout << "Domain length (L): " << L << std::endl;
    std::cout << "Output file prefix: " << output_prefix << std::endl;

    // Stability condition (for explicit schemes, good to check)
    double courant_number = alpha * dt / (dx * dx);
    std::cout << "Courant number (alpha * dt / dx^2): " << courant_number << std::endl;
    if (courant_number > 0.5)
    {
        std::cerr << "Warning: Courant number > 0.5. The explicit scheme might be unstable." << std::endl;
    }

    // --- Initial Conditions ---
    Eigen::VectorXd T_current(num_x);
    // Initial temperature profile: hot spot between x = 0.4 and x = 0.6
    for (int i = 0; i < num_x; ++i)
    {
        double x = (i + 1) * dx;
        if (x >= 0.4 && x <= 0.6)
        {
            T_current(i) = 100.0; // Initial hot region
        }
        else
        {
            T_current(i) = 0.0; // Other regions
        }
    }

    // --- Boundary Conditions (Neumann) ---
    double T_boundary_left = 0.0;
    double T_boundary_right = 0.0;

    std::cout << "\nInitial Temperature Profile:" << std::endl;
    printVector(T_current);

    // --- Create directory for results ---
    system("mkdir -p results");

    // --- Finite Difference Matrix ---
    // Construct fourth-order compact difference matrices
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(num_x, num_x);
    Eigen::MatrixXd B = Eigen::MatrixXd::Zero(num_x, num_x);

    // Interior points: fourth-order compact difference scheme
    // For interior point i, use the scheme:
    // (T_{i-1} + 4T_i + T_{i+1})/6 = (T_{i-1} - 2T_i + T_{i+1})/dx^2
    for (int i = 1; i < num_x - 1; ++i)
    {
        A(i, i - 1) = 1.0 / 6.0;
        A(i, i) = 4.0 / 6.0;
        A(i, i + 1) = 1.0 / 6.0;

        B(i, i - 1) = 1.0;
        B(i, i) = -2.0;
        B(i, i + 1) = 1.0;
    }

    // Boundary points: special treatment for adiabatic boundary conditions
    // At x=0: T_{-1} = T_1 (symmetry condition)
    A(0, 0) = 4.0 / 6.0;
    A(0, 1) = 2.0 / 6.0; // Using T_{-1} = T_1

    B(0, 0) = -2.0;
    B(0, 1) = 2.0; // Using T_{-1} = T_1

    // At x=L: T_{N+1} = T_{N-1} (symmetry condition)
    A(num_x - 1, num_x - 2) = 2.0 / 6.0; // Using T_{N+1} = T_{N-1}
    A(num_x - 1, num_x - 1) = 4.0 / 6.0;

    B(num_x - 1, num_x - 2) = 2.0; // Using T_{N+1} = T_{N-1}
    B(num_x - 1, num_x - 1) = -2.0;

    B = B / (dx * dx);

    // Construct Crank-Nicolson scheme matrices
    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(num_x, num_x);
    double factor = alpha * dt / 2.0;

    // Solve A * T^{n+1} = B * T^n
    // where A = I - factor * B
    //       B = I + factor * B
    Eigen::MatrixXd LHS = A - factor * B;
    Eigen::MatrixXd RHS = A + factor * B;

    // Precompute LU decomposition for efficiency
    Eigen::PartialPivLU<Eigen::MatrixXd> solver(LHS);

    // --- Time Stepping Loop ---
    Eigen::VectorXd T_next(num_x);
    std::vector<Eigen::VectorXd> T_history;
    T_history.push_back(T_current);

    for (int t = 0; t < num_t_steps; ++t)
    {
        // 计算右侧向量
        Eigen::VectorXd b = RHS * T_current;

        // 求解线性系统
        T_next = solver.solve(b);

        T_current = T_next;
        T_history.push_back(T_current);

        // Print progress
        if ((t + 1) % (num_t_steps / 10 == 0 ? 1 : num_t_steps / 10) == 0 || t == num_t_steps - 1)
        {
            std::cout << "Time step " << t + 1 << "/" << num_t_steps << " completed." << std::endl;
        }
    }

    // --- Output Results ---
    std::cout << "\nWriting results to files..." << std::endl;
    for (size_t t = 0; t < T_history.size(); ++t)
    {
        std::ofstream outfile(output_prefix + "_t_" + std::to_string(t) + ".csv");
        outfile << "x,Temperature\n";
        for (int i = 0; i < num_x; ++i)
        {
            outfile << (i + 1) * dx << "," << T_history[t](i) << "\n";
        }
        outfile.close();
    }

    // Write all timesteps to a single file for easier analysis
    std::ofstream all_timesteps(output_prefix + "_all_timesteps.csv");
    all_timesteps << "t,x,Temperature\n";
    for (size_t t = 0; t < T_history.size(); ++t)
    {
        for (int i = 0; i < num_x; ++i)
        {
            all_timesteps << t * dt << "," << (i + 1) * dx << "," << T_history[t](i) << "\n";
        }
    }
    all_timesteps.close();

    std::cout << "Simulation completed successfully." << std::endl;
    return 0;
}