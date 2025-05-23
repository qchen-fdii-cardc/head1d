# 一维热传导方程求解器

本项目实现了一个基于四阶紧致差分格式的一维热传导方程高精度数值求解示例。

![一维热传导](imgs/heat_conduction_2d_202505101317.gif)

## 项目结构

### 目录布局

```bash
heat1d/
├── src/                    # C++ 源代码目录
│   └── main.cpp           # 主程序入口
├── scripts/               # Python 脚本目录
│   ├── visualize.py       # 一维温度分布可视化
│   ├── visualize_2d.py    # 二维温度分布可视化
│   ├── compare_alpha.py   # 不同热扩散系数的对比
│   └── heat1d_solver.py   # Python 版本的热传导求解器
├── results/               # 模拟结果输出目录
│   └── YYYYMMDDHHMM/     # 时间戳命名的结果目录
│       ├── temperature_t_*.csv    # 各时间步的温度数据
│       └── temperature_all_timesteps.csv  # 所有时间步的汇总数据
├── imgs/                  # 可视化图片输出目录
│   └── *.gif             # 生成的动画文件
├── build/                # CMake 构建目录
├── .venv/                # Python 虚拟环境
├── CMakeLists.txt        # CMake 构建配置
├── LICENSE               # 许可证
├── README.md             # 项目文档
└── .gitignore            # 忽略文件
```

### 文件说明

1. 源代码文件：
   - `src/main.cpp`：实现四阶紧致差分格式的热传导方程求解器

2. Python 脚本：
   - `scripts/visualize.py`：生成一维温度分布随时间变化的动画
   - `scripts/visualize_2d.py`：生成包含一维曲线和二维热图的组合动画
   - `scripts/compare_alpha.py`：比较不同热扩散系数下的温度演化过程
   - `scripts/heat1d_solver.py`：Python 版本的热传导方程求解器

3. 输出目录：
   - `results/`：存储模拟结果
     - 使用时间戳（YYYYMMDDHHMM）创建子目录，避免文件覆盖
     - 每个时间步的温度数据保存为单独的 CSV 文件
     - 所有时间步的数据汇总保存在 `temperature_all_timesteps.csv`
   - `imgs/`：存储可视化结果
     - 生成的 GIF 动画文件使用时间戳命名
     - 支持自定义输出文件名和格式

4. 构建系统：
   - `build/`：CMake 生成的构建文件目录
   - `.venv/`：Python 虚拟环境，包含所有必要的 Python 包

### 文件命名规范

1. 模拟结果文件：
   - 格式：`temperature_t_<timestep>.csv`
   - 内容：包含位置和温度数据的 CSV 文件
   - 汇总文件：`temperature_all_timesteps.csv`

2. 可视化输出文件：
   - 一维动画：`heat_conduction_<timestamp>.gif`
   - 二维动画：`heat_conduction_2d_<timestamp>.gif`
   - 对比动画：`alpha_comparison_<timestamp>.gif`

### 数据格式

1. 温度数据文件（CSV 格式）：

   ```csv
   x,Temperature
   0.01,0.0
   0.02,0.0
   ...
   ```

2. 汇总数据文件（CSV 格式）：

   ```csv
   t,x,Temperature
   0.0,0.01,0.0
   0.0,0.02,0.0
   ...
   ```

## 环境配置

### 系统依赖

- C++20 或更高版本
- CMake 3.10 或更高版本
- Eigen3 3.3 或更高版本
- Python 3.x 及以下包：
  - numpy (< 2.0)
  - pandas
  - matplotlib
  - Pillow（用于生成 GIF）

#### 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-venv python3-pip
```

#### 安装 Eigen3

```bash
# Ubuntu/Debian
sudo apt-get install -y libeigen3-dev
```

### Python 环境配置

#### 安装 uv 包管理器

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 创建并激活虚拟环境

```bash
# 创建虚拟环境
uv venv .venv
source .venv/bin/activate

# 安装依赖
uv pip install "numpy<2" pandas matplotlib Pillow
```

#### 设置脚本执行权限

```bash
# 为 Python 脚本添加执行权限
chmod +x scripts/*.py
```

注意：所有 Python 脚本都使用 shebang 行 `#!./.venv/bin/python`，这确保了脚本使用项目虚拟环境中的 Python 解释器。

## 问题描述

### 控制方程

一维热传导方程如下：

$$
\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}
$$

其中：

- $T(x,t)$ 为温度
- $\alpha$ 为热扩散系数
- $x$ 为空间坐标
- $t$ 为时间

### 初始条件和边界条件

算例使用以下条件：

1. 初始条件：
   - $T(x,0) = 100^\circ \mathrm{C}$，当 $0.4 \leq x \leq 0.6$
   - $T(x,0) = 0^\circ \mathrm{C}$，其他位置

2. 边界条件：
   - $\frac{\partial T}{\partial x} = 0$ 在 $x=0$ 和 $x=L$ 处（绝热边界条件）
   - 这表示杆的两端没有热量流入或流出
   - 系统是封闭的，总热量守恒

## 数值格式

### 空间离散化

本项目使用四阶紧致差分格式进行空间离散，这是一种高精度的数值方法。

标准二阶中心差分格式的公式如下，通过三个点来近似二阶导数：

$$
\frac{\partial^2 T}{\partial x^2}\bigg|_i \approx \frac{T_{i-1} - 2T_i + T_{i+1}}{\Delta x^2} + O(\Delta x^2)
$$

四阶紧致差分格式是一种隐式方法，它通过构造关于二阶导数的线性方程组来获得更高精度的近似。其基本思想是：

在每个内部点 $i$ 处，我们不仅需要计算该点的二阶导数 $\left.\frac{\partial^2 T}{\partial x^2}\right\vert_i$，还需要考虑相邻点的二阶导数 $\left.\frac{\partial^2 T}{\partial x^2}\right\vert_{i-1}$ 和 $\left.\frac{\partial^2 T}{\partial x^2}\right\vert_{i+1}$。

通过泰勒展开和适当的系数选择，可以得到以下关系：

$$
\frac{1}{6}\left(\left.\frac{\partial^2 T}{\partial x^2}\right\vert_{i-1} + 4\left.\frac{\partial^2 T}{\partial x^2}\right\vert_i + \left.\frac{\partial^2 T}{\partial x^2}\right\vert_{i+1}\right) = \frac{1}{\Delta x^2}(T_{i-1} - 2T_i + T_{i+1}) + O(\Delta x^4)
$$

这个格式被称为"紧致"（compact）是因为：

- 它只使用相邻的三个点（$i-1$, $i$, $i+1$）来构造差分格式
- 虽然涉及二阶导数的隐式关系，但计算模板（stencil）保持紧凑
- 相比其他四阶格式（如五点显式格式），它使用更少的网格点就能达到四阶精度

在实际计算中：

- 需要求解一个三对角线性方程组来获得所有点的二阶导数值
- 这个方程组的形式为：$A \cdot \frac{\partial^2 T}{\partial x^2} = B \cdot T$
- 其中 $A$ 是包含系数 1/6, 4/6, 1/6 的三对角矩阵
- $B$ 是包含系数 1, -2, 1 的三对角矩阵（除以 $\Delta x^2$）

边界点处理（绝热边界条件）：

- 左边界 ($x=0$)：使用对称条件 $T_{-1} = T_1$
  - 矩阵 $A$ 的系数：$A_{0,0} = 4/6$, $A_{0,1} = 2/6$
  - 矩阵 $B$ 的系数：$B_{0,0} = -2$, $B_{0,1} = 2$
- 右边界 ($x=L$)：使用对称条件 $T_{N+1} = T_{N-1}$
  - 矩阵 $A$ 的系数：$A_{N-1,N-2} = 2/6$, $A_{N-1,N-1} = 4/6$
  - 矩阵 $B$ 的系数：$B_{N-1,N-2} = 2$, $B_{N-1,N-1} = -2$

这种格式的优点：

- 使用较少的网格点就能达到四阶精度
- 数值色散和耗散特性优于二阶格式
- 对高频分量的分辨率更好
- 计算模板紧凑，边界处理相对简单
- 通过预计算 LU 分解提高求解效率

其中 $\left.\frac{\partial^2 T}{\partial x^2}\right\vert_i$ 表示在点 $i$ 处的二阶导数

色散和耗散分析：

- 色散关系：
     $$\omega = \alpha k^2 \left[1 - \frac{(\Delta x)^2}{12}k^2 + O((\Delta x)^4)\right]$$
- 数值耗散：
  - 四阶格式的数值耗散比二阶格式小 $O((\Delta x)^2)$
  - 对于高频分量，耗散更小，保持更好的分辨率

### 时间离散化

使用 Crank-Nicolson 方法进行时间积分，这是一种无条件稳定的二阶精度格式。

时间离散格式：
   $$\frac{T^{n+1} - T^n}{\Delta t} = \frac{\alpha}{2}\left(\left.\frac{\partial^2 T}{\partial x^2}\right\vert^{n+1} + \left.\frac{\partial^2 T}{\partial x^2}\right\vert^n\right)$$

矩阵形式：
   $$(I - \frac{\alpha \Delta t}{2}A)T^{n+1} = (I + \frac{\alpha \Delta t}{2}A)T^n$$

   其中：

- $I$ 是单位矩阵
- $A$ 是空间离散化矩阵
- $T^n$ 是第 $n$ 个时间步的温度向量

稳定性分析：

- 放大因子：
     $$G(k) = \frac{1 - \frac{\alpha \Delta t}{2}k^2}{1 + \frac{\alpha \Delta t}{2}k^2}$$
- 无条件稳定：$\vert G(k) \vert \leq 1$ 对所有 $k$ 成立
- 相位误差：$O(\Delta t^2)$

色散和耗散特性：

- 时间离散不引入额外的数值耗散
- 相位误差随 $\Delta t$ 减小而减小
- 对于长时间模拟，保持能量守恒

### 数值精度

空间精度：

- 四阶紧致差分格式：$O(\Delta x^4)$
- 相比标准二阶格式：
  - 提高了温度梯度的分辨率
  - 减少了数值扩散
  - 更好地保持高频信息

时间精度：

- Crank-Nicolson 方法：$O(\Delta t^2)$
- 优点：
  - 无条件稳定
  - 能量守恒
  - 无数值耗散

总体精度：

- 空间和时间离散的组合精度：$O(\Delta x^4 + \Delta t^2)$
- 在合理的时间步长下，空间精度是主要限制因素

### 计算效率

矩阵求解：

- 使用 LU 分解预计算提高效率
- 每个时间步只需要一次矩阵求解
- 对于大规模问题，可以考虑使用稀疏矩阵存储

内存使用：

- 主要存储空间用于温度场和差分矩阵
- 对于大规模问题，可以使用稀疏矩阵格式

## 使用方法

### 编译

```bash
cmake -B build && cmake --build build
```

### 运行模拟

使用默认参数：

```bash
./build/heat1d_solver <num_x>
```

自定义参数：

```bash
./build/heat1d_solver --alpha <值> --dt <值> --time <值> <num_x>
```

参数说明：

- `--alpha`：热扩散系数（默认：0.01）
- `--dt`：时间步长（默认：0.01）
- `--time`：总模拟时间（默认：1.0）
- `--output`：输出文件前缀（默认：results/temperature）
- `num_x`：空间网格数（必需参数）

计算域说明：

- 计算域长度固定为 $L = 1.0$
- 空间步长 $dx$ 由 $L$ 和 $num_x$ 自动计算：$dx = L / (num_x + 1)$
- 网格点位置：$x_i = i \times dx$，其中 $i = 1, 2, ..., num_x$

### 可视化

生成结果动画：

```bash
# 方法1：直接运行（推荐）
# 由于脚本已设置正确的 shebang (#!./.venv/bin/python) 和执行权限，
# 可以直接运行脚本，无需手动激活虚拟环境
./scripts/visualize.py --alpha 0.01 --dt 0.002 --time 1.0 --num-x 100

# 方法2：手动激活虚拟环境
# 如果需要在运行脚本前执行其他 Python 命令，或使用其他 Python 工具，
# 可以手动激活虚拟环境
source .venv/bin/activate
./scripts/visualize.py --alpha 0.01 --dt 0.002 --time 1.0 --num-x 100

# 生成二维动画
./scripts/visualize_2d.py --alpha 0.01 --dt 0.002 --time 1.0 --num-x 100

# 比较不同热扩散系数
./scripts/compare_alpha.py --dt 0.002 --time 1.0 --num-x 100
```

关于虚拟环境激活的说明：

1. 直接运行（方法1）：
   - 优点：
     - 更简单，无需手动激活环境
     - 脚本始终使用正确的 Python 解释器
     - 避免环境变量污染
   - 适用场景：
     - 直接运行可视化脚本
     - 使用默认参数或通过命令行参数配置

2. 手动激活（方法2）：
   - 优点：
     - 可以在运行脚本前执行其他 Python 命令
     - 可以使用 Python 交互式环境
     - 可以使用其他 Python 工具（如 pip, uv 等）
   - 适用场景：
     - 需要调试或修改脚本
     - 需要安装新的 Python 包
     - 需要执行多个 Python 命令

可视化脚本参数说明：

- `--output`：输出 GIF 文件名（可选，默认使用时间戳）
- `--interval`：帧间隔（毫秒，默认：50）
- `--ymin`：Y轴最小值（可选）
- `--ymax`：Y轴最大值（可选）
- `--L`：计算域长度（默认：1.0）
- `--alpha`：热扩散系数（默认：0.01）
- `--dt`：时间步长（默认：0.002）
- `--time`：总模拟时间（默认：1.0）
- `--num-x`：空间网格数（默认：100）

注意：

1. 脚本会自动创建 `imgs` 目录用于保存生成的动画
2. 生成的 GIF 文件会自动添加时间戳以避免覆盖
3. 可视化脚本会自动计算合适的 Y 轴范围，也可以通过参数手动指定

## 结果与分析

### 结果展示

![alt text](imgs/heat_conduction_202505101402.gif)

生成的 GIF 动画展示：

- 温度随时间的变化
- 温度的空间分布
- 热量从初始高温区域平滑扩散
- 边界条件的正确处理

### 物理现象解释

模拟结果展示：

1. 初始温度分布：
   - 在 $x = 0.4$ 到 $x = 0.6$ 之间有一个 $100^\circ C$ 的矩形脉冲
   - 其他位置温度为零

2. 演化过程：
   - 热量从初始高温区域向外扩散
   - 温度梯度随时间逐渐平滑
   - 系统逐渐趋于热平衡

3. 主要特征：
   - 初始陡峭的温度梯度得到良好分辨
   - 总热量守恒
   - 后期温度分布平滑

4. 热扩散系数 $\alpha$ 的影响：
   - 较大的 $\alpha$ 值导致更快的热量扩散
   - 在初始温度不连续点（$x = 0.4$ 和 $x = 0.6$）可能出现数值振荡
   - 振荡原因：
     - 四阶紧致差分格式对高频分量（如温度不连续）的色散特性
     - 较大的 $\alpha$ 值放大了这种色散效应
     - 时间步长 $\Delta t$ 与空间步长 $\Delta x$ 的比值影响振荡的强度
   - 减小振荡的方法：
     - 适当减小时间步长
     - 增加空间网格点数
     - 使用更平滑的初始条件

## 许可证

本项目采用 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/katex.min.css"
    integrity="sha384-9eLZqc9ds8eNjO3TmqPeYcDj8n+Qfa4nuSiGYa6DjLNcv9BtN69ZIulL9+8CqC9Y" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/katex.min.js"
    integrity="sha384-K3vbOmF2BtaVai+Qk37uypf7VrgBubhQreNQe9aGsz9lB63dIFiQVlJbr92dw2Lx"
    crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/contrib/auto-render.min.js"
    integrity="sha384-kmZOZB5ObwgQnS/DuDg6TScgOiWWBiVt0plIRkZCmE6rDZGrEOQeHM5PcHi+nyqe"
    crossorigin="anonymous"></script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "\\[", right: "\\]", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false }
            ]
        });
    });
</script>

<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.esm.min.mjs';

    // 更新Mermaid配置
    const config = {
        startOnLoad: false,
        securityLevel: 'loose',
        theme: 'default',
        flowchart: {
            useMaxWidth: false,
            htmlLabels: true
        },
        class: {
            useMaxWidth: false,
            htmlLabels: true
        }
    };

    mermaid.initialize(config);

    // 添加渲染队列
    class RenderQueue {
        constructor() {
            this.queue = [];
            this.isProcessing = false;
        }

        add(task) {
            this.queue.push(task);
            if (!this.isProcessing) {
                this.process();
            }
        }

        async process() {
            if (this.queue.length === 0) {
                this.isProcessing = false;
                return;
            }

            this.isProcessing = true;
            const task = this.queue.shift();

            try {
                await task();
            } catch (error) {
                console.error('Error processing render task:', error);
            }

            setTimeout(() => this.process(), 0);
        }
    }

    const renderQueue = new RenderQueue();

    document.addEventListener("DOMContentLoaded", function () {
        const mermaidElements = document.querySelectorAll(".language-mermaid");

        mermaidElements.forEach((element, index) => {
            // 获取原始文本内容并清理
            const originalText = element.textContent.trim();

            // 替换所有HTML实体
            const processedText = originalText
                .replace(/&lt;/g, "<")
                .replace(/&gt;/g, ">")
                .replace(/--&gt;/g, "-->")
                .replace(/&lt;\|--/g, "<|--");

            // 创建新的容器
            const container = document.createElement('div');
            container.className = 'mermaid-container';

            // 创建控制按钮容器
            const controls = document.createElement('div');
            controls.className = 'mermaid-controls';

            // 创建缩放控制
            const zoomContainer = document.createElement('div');
            zoomContainer.className = 'zoom-controls';

            const zoomOutBtn = document.createElement('button');
            zoomOutBtn.textContent = '-';
            zoomOutBtn.className = 'zoom-btn';

            const zoomPercent = document.createElement('span');
            zoomPercent.textContent = '100%';
            zoomPercent.className = 'zoom-percent';

            const zoomInBtn = document.createElement('button');
            zoomInBtn.textContent = '+';
            zoomInBtn.className = 'zoom-btn';

            const autoFitBtn = document.createElement('button');
            autoFitBtn.textContent = '自动适应';
            autoFitBtn.className = 'zoom-btn';

            const exportBtn = document.createElement('button');
            exportBtn.textContent = '下载PNG';
            exportBtn.className = 'zoom-btn';

            // 创建Mermaid图表容器
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = processedText;

            // 创建源代码显示区域
            const details = document.createElement('details');
            const summary = document.createElement('summary');
            summary.textContent = '显示源代码';

            const pre = document.createElement('pre');
            pre.className = 'mermaid-source';
            pre.textContent = originalText;

            details.appendChild(summary);
            details.appendChild(pre);

            // 组装缩放控制
            zoomContainer.appendChild(zoomOutBtn);
            zoomContainer.appendChild(zoomPercent);
            zoomContainer.appendChild(zoomInBtn);
            zoomContainer.appendChild(autoFitBtn);
            zoomContainer.appendChild(exportBtn);

            // 组装控制按钮
            controls.appendChild(zoomContainer);

            // 组装所有元素
            container.appendChild(controls);
            container.appendChild(mermaidDiv);
            container.appendChild(details);

            // 替换原始元素
            element.parentNode.replaceChild(container, element);

            // 添加缩放事件监听
            let currentZoom = 100;
            const updateZoom = (newZoom) => {
                currentZoom = Math.max(50, Math.min(200, newZoom));
                const svg = mermaidDiv.querySelector('svg');
                if (svg) {
                    svg.style.transform = `scale(${currentZoom / 100})`;
                    svg.style.transformOrigin = 'top left';
                }
                zoomPercent.textContent = `${currentZoom}%`;
            };

            const autoFit = () => {
                updateZoom(100);
            };

            zoomInBtn.addEventListener('click', () => updateZoom(currentZoom + 10));
            zoomOutBtn.addEventListener('click', () => updateZoom(currentZoom - 10));
            autoFitBtn.addEventListener('click', autoFit);

            // 添加导出功能
            exportBtn.addEventListener('click', async () => {
                const svg = mermaidDiv.querySelector('svg');
                if (svg) {
                    try {
                        const scale = currentZoom / 100;
                        const pngUrl = await svgToPng(svg, scale);

                        const link = document.createElement('a');
                        link.download = `mermaid-diagram-${index + 1}.png`;
                        link.href = pngUrl;
                        link.click();
                    } catch (error) {
                        console.error('Error exporting diagram:', error);
                    }
                }
            });

            // 将渲染任务添加到队列
            renderQueue.add(async () => {
                try {
                    await mermaid.run({
                        nodes: [mermaidDiv],
                        suppressErrors: false
                    });

                    // 渲染完成后自动适应
                    const svg = mermaidDiv.querySelector('svg');
                    if (svg) {
                        const containerWidth = container.clientWidth;
                        const svgWidth = svg.getBoundingClientRect().width;
                        const newZoom = (containerWidth / svgWidth) * 100;
                        svg.style.transform = `scale(${Math.min(100, newZoom) / 100})`;
                        svg.style.transformOrigin = 'top left';
                    }
                } catch (error) {
                    console.error(`Error rendering diagram ${index + 1}:`, error);
                    mermaidDiv.innerHTML = `<div class="mermaid-error">Error rendering diagram: ${error.message}</div>`;
                }
            });
        });
    });
</script>

<script>
    // 添加 SVG 到 PNG 转换的辅助函数
    function svgToPng(svg, scale = 1) {
        return new Promise((resolve, reject) => {
            try {
                // 创建临时 SVG 元素
                const tempSvg = svg.cloneNode(true);

                // 获取原始尺寸
                const bbox = svg.getBBox();
                const width = bbox.width * scale;
                const height = bbox.height * scale;

                // 设置临时 SVG 的属性
                tempSvg.setAttribute('width', width);
                tempSvg.setAttribute('height', height);
                tempSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);

                // 复制所有样式和内联样式
                const styles = window.getComputedStyle(svg);
                const styleText = Array.from(styles).map(prop =>
                    `${prop}: ${styles.getPropertyValue(prop)}`
                ).join('; ');
                tempSvg.setAttribute('style', styleText);

                // 复制所有子元素的样式
                const copyStyles = (source, target) => {
                    const sourceChildren = source.children;
                    const targetChildren = target.children;

                    for (let i = 0; i < sourceChildren.length; i++) {
                        const sourceChild = sourceChildren[i];
                        const targetChild = targetChildren[i];

                        if (sourceChild && targetChild) {
                            const childStyles = window.getComputedStyle(sourceChild);
                            const childStyleText = Array.from(childStyles).map(prop =>
                                `${prop}: ${childStyles.getPropertyValue(prop)}`
                            ).join('; ');
                            targetChild.setAttribute('style', childStyleText);

                            copyStyles(sourceChild, targetChild);
                        }
                    }
                };

                copyStyles(svg, tempSvg);

                // 转换为数据 URL
                const svgData = new XMLSerializer().serializeToString(tempSvg);

                // 创建图片元素
                const img = new Image();
                img.crossOrigin = 'anonymous';

                img.onload = () => {
                    try {
                        // 创建画布
                        const canvas = document.createElement('canvas');
                        canvas.width = width;
                        canvas.height = height;

                        // 绘制到画布
                        const ctx = canvas.getContext('2d');
                        ctx.fillStyle = '#f8f8f8';
                        ctx.fillRect(0, 0, width, height);

                        // 使用 drawImage 绘制 SVG
                        ctx.drawImage(img, 0, 0, width, height);

                        // 转换为 PNG
                        const pngUrl = canvas.toDataURL('image/png');

                        resolve(pngUrl);
                    } catch (error) {
                        reject(error);
                    }
                };

                img.onerror = (error) => {
                    reject(error);
                };

                // 使用 data URL
                const svgDataUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
                img.src = svgDataUrl;
            } catch (error) {
                reject(error);
            }
        });
    }
</script>

<style>
    .mermaid-container {
        margin: 1em 0;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
    }

    .mermaid-controls {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin-bottom: 0.5em;
    }

    .zoom-controls {
        display: flex;
        align-items: center;
        gap: 0.5em;
    }

    .zoom-btn {
        padding: 0.25em 0.5em;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #fff;
        cursor: pointer;
    }

    .zoom-btn:hover {
        background: #f5f5f5;
    }

    .zoom-percent {
        min-width: 3em;
        text-align: center;
    }

    .mermaid {
        background: #f8f8f8;
        padding: 1em;
        border-radius: 4px;
        margin-bottom: 0.5em;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
    }

    .mermaid svg {
        transition: transform 0.2s ease;
        max-width: 100%;
        height: auto;
    }

    .mermaid-source {
        background: #f0f0f0;
        padding: 1em;
        border-radius: 4px;
        margin-top: 0.5em;
        white-space: pre-wrap;
        font-family: monospace;
    }

    .mermaid-error {
        color: red;
        padding: 1em;
        background: #fff0f0;
        border: 1px solid #ffcccc;
        border-radius: 4px;
    }

    details {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 0.5em;
    }

    summary {
        cursor: pointer;
        padding: 0.5em;
        background: #f5f5f5;
        border-radius: 4px;
    }

    summary:hover {
        background: #e9e9e9;
    }
</style>
