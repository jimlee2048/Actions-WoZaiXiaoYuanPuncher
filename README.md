# WoZaiXiaoYuanPuncher-Actions

我在校园自动打卡程序：[zimin9/WoZaiXiaoYuanPuncher](https://github.com/zimin9/WoZaiXiaoYuanPuncher) 的 Github Action 版。

基于原仓库中 [@Chorer](https://github.com/Chorer) 贡献的腾讯云函数版脚本修改。

如果在执行脚本时，总是遇到提示`用户或密码错误，还可尝试*次`，导致无法正常打卡的问题，请参考文末[常见问题](#常见问题)。

## 更新日志

- 2021.10.8  新增 支持钉钉机器人推送.

  > 🎉 感谢 [@baifan97](https://github.com/baifan97) 的贡献！

- 2021.09.28 修复无法更新 jwsession 的问题。

- 2021.09.19 新增 支持多账户。
  
  **⚠重要提醒：** 该版本对配置文件中调用配置的默认参数进行了修改，请旧有用户 Fetch 最新代码后，删除原有的 Secret 和 Environment，并参考新的文档重新配置所有参数。

- 2021.09.03 新增 支持喵推送。

- 2021.08.04 新增 支持多种通知方式（Serverchan-Turbo、PushPlus、Bark）。

  > 🎉 感谢 [@LeslieLeung](https://github.com/LeslieLeung) 的贡献！

## 关于本脚本

- 添加脚本 `wzxy-healthcheck.py`，适配部分学校的打卡项目“健康打卡”。

  > 关于本项目中的两个脚本：
  >
  > - `wzxy-dailyreport.py`，对应打卡项目“日检日报”（一天多时段打卡，需要提交位置信息与体温信息）。
  >
  > - `wzxy-healthcheck.py`，对应打卡项目“健康打卡”（一天只需打卡一次，仅需提交位置信息）。
  >
  > 两个脚本请按需启用，详见下方使用指南。

- 利用 [actions/cache@v2](https://github.com/marketplace/actions/cache) 实现缓存 jwsession，避免频繁登录可能导致的账号登录问题。

- 利用 Github Action 的 [Secrets](https://docs.github.com/cn/actions/reference/encrypted-Secrets) 加密储存所有配置信息，任何人都无法从项目仓库中直接读取这些敏感信息。

- 支持多用户/多地点打卡，利用 Github Action 的 [Environment](https://docs.github.com/cn/actions/reference/environments) 实现多配置文件的储存。

- 对原代码部分逻辑结构进行修改优化。

- 支持多种通知方式（Serverchan-Turbo、PushPlus、Bark、喵推送）

欢迎 Issue & Pull request ！

## 使用指南

### Step0 准备工作

- 对小程序进行抓包，抓取自己的打卡数据，请参见文末[抓包教程](#抓包教程)。
- 在小程序 我的-设置 中修改自己的密码。
  - 注意要6-12位
  - 修改完成后请勿马上重新登陆

### Step1 Fork本仓库

![](https://i.loli.net/2021/08/07/CXA4LBzFKxpkYj8.png)

- 点击本仓库页面中右上角的 `Fork` 按钮。

- 稍等片刻，将自动跳转至新建的仓库。

### Step2 配置打卡参数

> 如需配置多用户，请参考文末“其他需求”中的介绍。


- 在新建的仓库页面，点击选项 `Settings`，进入项目仓库设置页面。

- 在左方侧边栏点击选项 `Environments`，点击右上角按钮 `New environment` 创建用于存放用户配置的 Environment `WZXY_CONFIG_01`。

![](https://i.loli.net/2021/08/07/jPYLRtgVk27KAUl.png)

- 进入新建的 Environment ，在 “Environment Secrets” 一栏中点击 `Add Secret` 按钮，新建以下 Secret，并填写对应 Value 值：

  - `USERNAME`：我在校园账号的用户名。

  - `PASSWORD`：我在校园账号的密码。

  - `CACHE_NAME`：值任意，用于储存 jwsession 的缓存文件的前缀名。为避免信息泄露，建议使用包含数字与大小写英文的无序字符串，且长度在32位以上（可以尝试键盘乱打 or 使用生成器）。

    > 请注意：配置多账户打卡时，不同环境中的`CACHE_NAME`不能相同！！

  - `TEMPERATURE`（可选）：打卡提交体温信息时使用的体温值，数值要求精确到1位小数。可以仅指定一个温度值（例：`36.0`），也可以指定温度值范围，两个温度值间使用符号`~`连接（例：`36.1~36.4`），打卡时将随机从指定的范围中选取一个值作为体温数据提交。如不创建该 Secret，脚本将使用默认值`36.0~36.5`。
  
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
  > - 出于学校要求，两个打卡项目所需提交的地理位置信息可能不一样（比如“日检日报”在校打卡，“健康打卡”在家打卡），可以分别抓取两个打卡项目的提交数据，据此根据打卡项目分别配置两个 Environment 的 Secrets。
  
  - `SCT_KEY`（可选）：填写自己 [Serverchan-Turbo](https://sct.ftqq.com/sendkey) 的 SendKey，用于 Serverchan-Turbo 推送打卡结果的通知。
  
  - `BARK_TOKEN` （可选）：填写自己 Bark 的推送 URL，建议从 Bark 客户端复制，形如`http://yourdomain.name/thisisatoken`，用于 Bark 推送打卡结果的通知。请注意不要以斜杠结尾。
  
  - `PUSHPLUS_TOKEN`（可选）：填写自己 [PushPlus](https://www.pushplus.plus/) 的 token，用于 PushPlus 推送打卡结果的通知。
  
  - `MIAO_CODE` （可选）：填写 [喵提醒](https://miaotixing.com/) 的喵码，需要先创建提醒获取，具体见喵推送公众号，用于 喵提醒 推送打卡结果的通知。

  - `DD_BOT_ACCESS_TOKEN`（可选）：钉钉机器人推送 Token，填写机器人的 Webhook 地址中的 token。只需 https://oapi.dingtalk.com/robot/send?access_token=XXX 等于=符号后面的XXX即可。

  - `DD_BOT_SECRET`（可选）：钉钉机器人推送SECRET。[官方文档](https://developers.dingtalk.com/document/app/custom-robot-access) 
  
  > 如需配置钉钉机器人，上述的 `DD_BOT_ACCESS_TOKEN` 和 `DD_BOT_SECRET` 两条 Secrect 都需创建。

  > **推送通知的补充说明**
  >
  > 目前支持四种推送方式（PushPlus、Serverchan-Turbo、Bark、钉钉机器人）：
  >
  > - 需要使用哪一种方式推送，创建该方式对应的 Secret 即可。
  >
  > - 你也可以同时创建对应不同推送方式的多个 Secret，这将同时推送所对应的多个渠道。
  >
  > - 如不创建这些推送方式对应的 Secret，则不会推送打卡结果通知。

### Step3 配置脚本运行时间

脚本的触发运行时间由项目仓库内`.github/workflows`的两个 Workflow 文件配置：

- `wzxy_dailyreport.yml`

  - 对应脚本“`wzxy-dailyreport.py`”（打卡项目“日检日报”）。
  
  - 默认在每天北京时间 0:30 执行。
  
- `wzxy_healthcheck.yml`

  - 对应脚本“`wzxy-healthcheck.py`”（打卡项目“健康打卡”）。
  
  - 默认在每天北京时间 7:30 和 20:30 执行。

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
    > - **注意：** Github Actions 用的是世界标准时间（UTC），北京时间（UTC+8）转换为世界标准时需要减去8小时

- 修改完成后，点击页面右侧绿色按钮 `Start commit`，然后点击绿色按钮 `Commit changes`。

  > **注意：**出于开发者个人使用需要，`wzxy_healthcheck.yml`里`environment`参数默认为`environment: WZXY_CONFIG_02`；如果你严格按照上述教程操作且没有多账户/多地点打卡需要，请找到该行代码并将02改为01。
  > 关于多账户，请参考文末“其他需求”

### Step4 手动测试脚本运行

- 点击页面上方选项 `Actions`，进入 Github Actions 配置页面。

- 左侧边栏点击需要测试的脚本：

  - `WZXY_DailyReport`：对应脚本“`wzxy-dailyreport.py`”，打卡项目“日检日报”。

  - `WZXY_HealthCheck`：对应脚本“`wzxy-healthcheck.py`”，打卡项目“健康打卡”。

以测试 `WZXY_DailyReport` 为例：

![](https://i.loli.net/2021/08/07/qWERC7NUDuvxPd2.png)

- 在未自行打卡的打卡时段，点击右侧按钮 `Run workflow`，再次点击绿色按钮 `Run workflow`。

- 等待几秒后刷新页面。

- 2分钟后登入我在校园小程序；如无意外，打卡将被完成；如果你正确配置了 PUSH_TOKEN，应同时在2分钟内收到微信消息推送。

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
>
> - 点击搜索栏右边的 `...` 按钮，然后点击 `Disable workflow`。

## 常见问题

1. 即便所配置的密码正确，脚本执行时仍然提示`用户名或密码错误，还可尝试*次`？
   - 在小程序中重新修改密码。
   - 修改密码后不要马上在小程序上重新登陆。
   - 更新对应用户配置文件中的 Secret `PASSWORD`，填写新密码。
   - 再次尝试运行脚本，查看是否正常登陆并获取 jwsession。
   - 如仍有问题，请在确保配置文件中密码信息正确的后提 issue。


2. 如何配置多账户/多地点打卡？

   - 参照 Step 2，新建并配置另一环境；环境名建议保持`WZXY_CONFIG_**`的格式。

   - 参考 Step 3，打开打卡脚本所对应的 workflow 文件，复制末尾的多账户配置示例代码，注销注释后填写另一配置的环境名即可。
3. 需要其他推送通知渠道？
   - 请提 issue 或参考代码自行实现。
4. 其他问题？
   - 欢迎提 issue。

## 抓包大致方法

![](https://i.loli.net/2021/08/07/VBrtzGnQEJc5XF4.png)

- 在电脑上安装配置好 Fiddler。

- 启动微信电脑版和 Fiddler，打开我在校园小程序，先手动打卡一次日检日报/健康打卡。

- 提交打卡信息的同时观察 Fiddler 左侧栏中最新出现的 Host 为 `student.wozaixiaoyuan.com` 的信息（如果打卡的是日检日报，URL 为`/heat/save.json`；健康打卡则为`/health/save.json"`）。

- 双击打开这条信息，然后点击右侧上方的 `WebForms` 一栏，对照显示抓取到的信息填写 Environment Secrets 就可以了。

- Fiddler 配置与抓包操作参考：

  - [Chaney1024/wozaixiaoyuan](Chaney1024/wozaixiaoyuan)
  
  - [Duangdi/fuck-wozaixiaoyuan](https://github.com/Duangdi/fuck-wozaixiaoyuan/blob/master/%E4%B8%80%E6%97%A5%E4%B8%89%E6%A3%80%E8%87%AA%E5%8A%A8%E6%89%93%E5%8D%A1.pdf)
  
  - [Liuism/xsyu-wzxy-sign](https://github.com/Liuism/xsyu-wzxy-sign)

## 参考/致谢

- [zimin9/WoZaiXiaoYuanPuncher](https://github.com/zimin9/WoZaiXiaoYuanPuncher)

- [Chorer/WoZaiXiaoYuanPuncher-cloudFunction](https://github.com/Chorer/WoZaiXiaoYuanPuncher-cloudFunction)

- [why20hh/WoZaiXiaoYuan-SVTCC](https://github.com/why20hh/WoZaiXiaoYuan-SVTCC) ，健康打卡脚本参考了其代码。

- [@LeslieLeung](https://github.com/LeslieLeung) ，贡献了对多种通知方式（Serverchan-Turbo、PushPlus、Bark）的支持。

## 声明

- 本项目仅供编程学习/个人使用，请遵守Apache-2.0 License开源项目授权协议.

- 请在国家法律法规和校方相关原则下使用。

- 开发者不对任何下载者和使用者的任何行为负责。

- 程序使用的所有信息均利用 Github 的 [Secrets](https://docs.github.com/cn/actions/reference/encrypted-Secrets) 加密储存。

