# WoZaiXiaoYuanPuncher-Actions
我在校园自动打卡程序：[zimin9/WoZaiXiaoYuanPuncher](https://github.com/zimin9/WoZaiXiaoYuanPuncher) 的 Github Action 版。

基于原仓库中 [@Chorer](https://github.com/zimin9/WoZaiXiaoYuanPuncher/commits?author=Chorer) 贡献的腾讯云函数版脚本修改。

我的工作：

- 新增脚本 `wzxy-healthcheck.py`，适配部分学校的打卡项目“健康打卡”。

  > 关于本项目中的两个脚本：
  >
  > - `wzxy-dailyreport.py`，对应打卡项目“日检日报”（一天多时段打卡，需要提交位置信息与体温信息）。
  >
  > - `wzxy-healthcheck.py`，对应打卡项目“健康打卡”（一天只需打卡一次，仅需提交位置信息）。
  >
  > 两个脚本请按需启用，详见下方使用指南。

- 利用 [actions/cache@v2](https://github.com/marketplace/actions/cache) 实现缓存 jwsession，避免频繁登录可能导致的账号登录问题。

- 利用 Github Action 的 [Secrets](https://docs.github.com/cn/actions/reference/encrypted-secrets) 加密储存所有配置信息，任何人都无法从项目仓库中直接读取这些敏感信息。

- 利用 Github Action 的 [Environment](https://docs.github.com/cn/actions/reference/environments) 实现多个打卡地理数据的储存。

- 对原代码部分逻辑结构进行修改优化。

欢迎 Issue & Pull request ！

## 使用指南

### Step1 Fork本仓库

![](https://i.loli.net/2021/08/07/CXA4LBzFKxpkYj8.png)

- 点击本仓库页面中右上角的 `Fork` 按钮。
- 稍等片刻，将自动跳转至新建的仓库。

### Step2 配置打卡参数

![](https://i.loli.net/2021/08/07/SEOhnMIevTAF6ou.png)

- 在新建的仓库页面，点击选项 `Settings`，进入项目仓库设置页面。
- 在左方侧边栏点击页面上方选项 `Secrects`，点击右上方按钮 `New repository secret`, 新建以下 Secrect，并填写对应 Value 值：
  - `USERNAME`：我在校园账号的用户名。
  - `PASSWORD`：我在校园账号的密码。
  - `CACHE_NAME`：值任意，用于储存 jwsession 的缓存文件的前缀名。为避免信息泄露，建议使用包含数字与大小写英文的无序字符串，且长度在32位以上（可以尝试键盘乱打 or 使用生成器）。
  - `PUSH_TOKEN`（可选）：填写自己 [pushplus](https://www.pushplus.plus/) 的 token，用于微信推送脚本执行自动打卡结果的通知。如不创建该 Secrect，则关闭推送通知功能。
  - `TEMPERATURE`（可选）：打卡提交体温信息时使用的体温值，数值要求精确到1位小数。可以仅指定一个温度值（例：`36.0`），也可以指定温度值范围，两个温度值间使用符号`~`连接（例：`36.1~36.4`），打卡时将随机从指定的范围中选取一个值作为体温数据提交。如不创建该 Secrect，脚本将使用默认值`36.0~36.5`。

![](https://i.loli.net/2021/08/07/zmQnwv64SUbo8YZ.png)

- 在左方侧边栏点击选项 `Environments`，点击右上角按钮 `New environment` 创建打卡地理数据存放的 Environment。
  - `WZXY_POSITION_DR`（打卡项目“日检日报”，对应脚本“`wzxy-dailyreport.py`”，对应 Workflow “`WZXY_DailyReport`”）。
  - `WZXY_POSITION_HC`（打卡项目“健康打卡”，对应脚本`wzxy-healthcheck.py`，对应 Workflow “`WZXY_HealthCheck`”）。

  > 如果你无需用到其中任一脚本，你不必创建该脚本的对应环境。
  >
  > 同时，你还需要关闭该脚本对应的 Workflow，详见 Step4。

![](https://i.loli.net/2021/08/07/jPYLRtgVk27KAUl.png)

- **分别**进入这两个新建的 Environment ，在 “Environment secrets” 一栏中点击 `Add Secrect` 按钮，新建以下 Secrect，并填写对应 Value 值：

  - `LATITUDE`：打卡该项目时所提交位置信息的纬度，对应抓包信息中的 “latitude”。

  - `LONGITUDE`：打卡该项目时所提交位置信息的经度，对应抓包信息中的 “longitude”。

  - `COUNTRY`：打卡该项目时所提交位置信息的经度，对应抓包信息中的 “country”。

  - `CITY`：打卡该项目时所提交位置信息的市，对应抓包信息中的 “city”。

  - `DISTRICT`：打卡该项目时所提交位置信息的区，对应抓包信息中的 “district”。

  - `PROVINCE`：打卡该项目时所提交位置信息的省，对应抓包信息中的 “province”。

  - `TOWNSHIP`：打卡该项目时所提交位置信息的街道，对应抓包信息中的 “township” 。

  - `STREET`：Value 值填写 打卡该项目时所提交位置信息的路，对应抓包信息中的 “street”。

  > - 由于不同的学校情况与实际需求，以上数据需要自行抓取。
  >
  > - 出于学校要求，两个打卡项目所需提交的地理位置信息可能不一样（比如“日检日报”在校打卡，“健康打卡”在家打卡），可以分别抓取两个打卡项目的提交数据，据此根据打卡项目分别配置两个 Environment 的 Secrects。

<details>
<summary>抓包大致方法</summary>
<a href="https://sm.ms/image/VBrtzGnQEJc5XF4" target="_blank"><img src="https://i.loli.net/2021/08/07/VBrtzGnQEJc5XF4.png" ></a>

- 在电脑上安装配置好 Fiddler。
- 启动微信电脑版和 Fiddler，打开我在校园小程序，先手动打卡一次日检日报/健康打卡。
- 提交打卡信息的同时观察 Fiddler 左侧栏中最新出现的 Host 为 `student.wozaixiaoyuan.com` 的信息（如果打卡的是日检日报，URL 为`/heat/save.json`；健康打卡则为`/health/save.json"`）。
- 双击打开这条信息，然后点击右侧上方的 `WebForms` 一栏，对照显示抓取到的信息填写 Environment Secrects 就可以了。
-  Fiddler 配置与抓包操作参考：

  - [Chaney1024/wozaixiaoyuan](Chaney1024/wozaixiaoyuan)
  - [Duangdi/fuck-wozaixiaoyuan](https://github.com/Duangdi/fuck-wozaixiaoyuan/blob/master/%E4%B8%80%E6%97%A5%E4%B8%89%E6%A3%80%E8%87%AA%E5%8A%A8%E6%89%93%E5%8D%A1.pdf)
  - [Liuism/xsyu-wzxy-sign](https://github.com/Liuism/xsyu-wzxy-sign)

</details>

### Step3 配置脚本运行时间

脚本的触发运行时间由项目仓库内`.github/workflows`的两个 Workflow 文件配置：

- `wzxy_dailyreport.yml`
  - 对应脚本“`wzxy-dailyreport.py`”（打卡项目“日检日报”）。
  - 默认在每天北京时间 0:30 执行。
- `wzxy_healthcheck.yml`
  - 对应脚本“`wzxy-healthcheck.py`”（打卡项目“健康打卡”）。
  - 默认在每天北京时间  7:30 和 20:30 执行。

如果需要修改脚本的运行时间：

![](https://i.loli.net/2021/08/07/dNeS2igbwKmPzCO.png)

- 点击页面上方选项 `Code`，回到项目仓库主页。

- 点击文件夹`.github/workflows`，修改所需要的 Workflow 文件。

  以修改`wzxy_dailyreport.yml`为例：

  - 点击`wzxy_dailyreport.yml`，进入文件预览。

  - 点击预览界面右上方笔的图标，进入编辑界面。

    ![](https://i.loli.net/2021/08/07/mvgOB824MsdZ1up.png)

  - 根据自己的打卡时间需要，修改代码中的 cron 表达式：

    ![](https://i.loli.net/2021/08/07/ntImHFAeu6TM7zK.png)

    > - cron是个啥？百度一下！
    >
    > - 注意：Github Actions 用的是世界标准时间（UTC），北京时间（UTC+8）转换为世界标准时需要减去8小时

- 修改完成后，点击页面右侧绿色按钮 `Start commit`，然后点击绿色按钮 `Commit changes`。

### Step4 手动测试脚本运行

- 点击页面上方选项 `Actions`，进入 Github Actions 配置页面。
- 左侧边栏点击需要测试的脚本：
  - `WZXY_DailyReport`：对应脚本“`wzxy-dailyreport.py`”，打卡项目“日检日报”。
  - `WZXY_HealthCheck`：对应脚本“`wzxy-healthcheck.py`”，打卡项目“健康打卡”。

以测试 `WZXY_DailyReport` 为例：

![](https://i.loli.net/2021/08/07/qWERC7NUDuvxPd2.png)

- 在未自行打卡的打卡时段，点击右侧按钮 `Run workflow`，再次点击绿色按钮 `Run workflow`。

- 等待几秒后刷新页面。

- 2分钟后登入我在校园小程序；如无意外，打卡将被完成；如果你正确配置了 PUSH_TOKEN，应当同时在2分钟内收到微信消息推送。

- 如果出现以下情况：

  - 2分钟后仍未自动打卡。
  - Github Actions 界面最新的 workflow run `WZXY_HealthCheck` 状态为红色错误。
  - 以及其他错误情况。

  请在Github Actions 配置界面中，打开最新的 Workflow run `WZXY_HealthCheck`，查看错误日志，并检查自己的参数配置是否正确。

> 两个脚本对应的 Workflow 都默认开启定时执行任务，如果你无需使用/需要暂时停用某一脚本，请参照以下步骤停用其对应的 Workflow：
>
> ![](https://i.loli.net/2021/08/07/W23K7Gqzsra59Xf.png)
>
> - 在 Github Actions 配置页面中，左侧边栏选择需要停用的脚本所对应的 Workflow。
> - 点击搜索栏右边的 `...` 按钮，然后点击 `Disable workflow`。

## 参考/鸣谢

- [zimin9/WoZaiXiaoYuanPuncher](https://github.com/zimin9/WoZaiXiaoYuanPuncher)
-  [@Chorer](https://github.com/zimin9/WoZaiXiaoYuanPuncher/commits?author=Chorer) 
- [why20hh/WoZaiXiaoYuan-SVTCC](why20hh/WoZaiXiaoYuan-SVTCC)

## 声明

- 本项目仅供编程学习/个人使用，请遵守Apache-2.0 License开源项目授权协议
- 请在国家法律法规和校方相关原则下使用
- 开发者不对任何下载者和使用者的任何行为负责
- 无任何后门，也不获取、存储任何信息

