# UP80代码、结果与离线使用（完整输入包的补充）

与12份UP80_INPUT包共同使用：全部解压到同一个空目录。本补充包保留经过实际空目录离线验收的源码、结果CSV/15份矩阵JSON、独立审计和完整静态查询网页；不重复输入包或可重建的大NPZ。不要把本包单独理解为包含全部研究输入。

## 已验证范围
Python3.12.14/x86_64、NumPy2.3.5、pandas2.2.3：完整离线重建530.56秒；每10秒采样的工作目录分配空间峰值4,952,297,472字节（不是全局瞬时峰值保证）。15JSON、15CSV逐字节相同，15NPZ内部数组精确相同；冻结5554股base与5N补丁各5554份gzip逐字节相同，metadata无忽略。输入原始供应商数据、冻结查询基线均不改。

Mac Python3.13/ARM尚未实测；不得宣称跨平台结果已验证。18GB剩余空间须先检查下载/解压/独立工作目录与系统余量。本平台约4.61GiB工作空间采样值不等于任何机器峰值保证。

## 离线重建
先按各包SHA256SUMS校验ZIP，再用各自核验器检查文件；输入与结果使用各自独立清单和核验器，数据目录解压同一根。详见up80_recovery/offline_rebuild/README.md。

```sh
python3 up80_recovery/offline_rebuild/run_offline.py --package-root . --work-root ../new_empty_rebuild
# 上条默认只检查并展示计划；确认依赖及磁盘后：
python3 up80_recovery/offline_rebuild/run_offline.py --package-root . --work-root ../new_empty_rebuild --execute
```

不要自动联网安装依赖；requirements.txt记录已验证版本。全部股票/日期/分组/缺失位置必须一致；文件SHA差异单独报告，不能用浮点容忍掩盖。聚合浮点既有比较规则绝对误差1e-12、相对0；超差不自动放宽。源代码中补充独立审计脚本可能依赖额外中间结果，正式便携入口为上述run_offline，不是每个历史脚本均可独立运行。

## 本地看网页
前端冻结提交00621cda1af331e788f57e0e6c626515b05d9532，仅静态文件，不含部署身份或管理信息。网页按需fetch单股gzip，不能双击file://保证完整功能。

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory sites/shareholder-matrix/dist
```

浏览器打开http://127.0.0.1:8000，仅绑定本机。5554查询是旧冻结base+5N补丁的规则迁移，不是重新从全部供应商原始数据构造5554股。

## 证据与限制
原始1494旧事件档不可得，不能宣称逐成员验证旧1494；旧972可核，旧15曲线回归及独立路径/特征/新1620格/分期审计通过。统计日起点含事后信息，选池存续偏差和首次公开时间未逐条原文核验的限制仍保留，历史规律不保证未来收益。第三方来源权利说明见up80_recovery/SOURCES_AND_RIGHTS_ZH.md。

源文件不修改。少量历史绝对路径在归档副本净化，FILE_MANIFEST同时列源SHA/包SHA，PATH_REDACTIONS逐项说明；原始数字及股票公司名不删。代码冻结清单保留原SHA用于对应实际验收版本。最终核验需分别识别原源字节和仅路径净化后的包字节。
