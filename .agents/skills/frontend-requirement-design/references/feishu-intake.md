# 飞书需求读取

## 固定读取方式

飞书需求、技术文档和 Wiki 链接统一用 CLI 读取，不用浏览器抓取：

```bash
lark-cli docs +fetch --doc '<feishu-url>' --doc-format markdown --detail simple --as user
```

命令返回的就是本次读取内容；需要长期复用时保存为快照。`fetch_feishu.py` 只是这条命令的包装，不能绕过 CLI 登录态。

## 登录态过期

如果命令返回 `need_user_authorization` 或 `token_missing`，说明 `lark-cli` 的 user token 过期，不是文档无权限：

```bash
lark-cli auth login --scope "docx:document:readonly" --no-wait --json
```

打开返回的 `verification_url` 完成授权，然后执行：

```bash
lark-cli auth login --device-code '<device_code>'
```

授权完成后重新执行拉取命令。不要把 cookie、token 或 device code 写进需求文档。

### 运行环境

- `lark-cli` 必须在沙箱外执行（macOS 钥匙串可写）。在沙箱里运行可能出现 `keychain Set failed: operation not permitted`。
- 出现 keychain 写失败时，不要连续重试；刷新令牌可能已经被消耗。改到沙箱外重新走一次授权。
- 不要同时展示多个 `device_code`。上一个授权链接没完成时，重新生成会让旧链接失效。

### 需要额外 scope 的情况

`--recommend` 不包含云盘读取和文件夹权限。需要读取文件夹、创建到指定目录时，额外申请：

```bash
lark-cli auth login --recommend \
  --scope "drive:drive space:document:retrieve" \
  --no-wait --json
```

创建文档还需要 `docx:document:create`；更新已有文档需要 `docx:document:write_only`。授权完成后先执行 `lark-cli auth status`，确认 `user` 是 `ready`。

## 拉取文档

已登录后执行上面的 `lark-cli docs +fetch`，再把结果保存到快照。

需要包含评论或 block 细节时，先看 `lark-cli docs +fetch --help`，不要猜参数。

## 保存快照

保存到：

```text
docs/<feature>/sources/feishu-<doc-name>.md
```

文件开头记录：

```markdown
> 来源：<feishu-url>
> 获取时间：<YYYY-MM-DD HH:mm>
> 读取范围：<全文 / 章节>
```

需要时再保存附件或截图；不要把登录凭据、cookie 或 token 写进文档。

## 发布和更新文档

本地 Markdown 确认后，再创建或更新飞书文档：

```bash
# 创建到指定文件夹
lark-cli docs +create --title '<标题>' --content @./docs/<feature>/<file>.md \
  --doc-format markdown --parent-token '<folder-token>' --as user

# 追加到已有文档
lark-cli docs +update --doc '<doc-url-or-token>' --command append \
  --content @./docs/<feature>/<file>.md --doc-format markdown --as user
```

创建前先确认标题和目标文件夹；更新已有文档时不要把 `append` 写成 `overwrite`。发布成功后把文档 URL 写进 `workflow-state.yaml` 的 `feishu.documents`。

## 提取顺序

1. 背景和目标；
2. 用户/角色和使用场景；
3. 页面、入口和跳转；
4. 表单、列表、字段和校验；
5. 权限和可见性；
6. 空值、异常、重试和兼容；
7. 验收标准和明确不做；
8. 需求中的接口、数据或后端依赖；
9. 文档之间的冲突。

## 事实与假设

每个关键结论标来源：

- `[文档]`：需求文档明确写；
- `[代码]`：现有实现确认；
- `[用户确认]`：用户明确回答；
- `[假设]`：为了继续设计暂时采用，必须让用户确认。

同一件事同时有 `[文档]` 和 `[代码]` 且冲突时，先记录冲突，不要静默选择。

## 读不到时

- 文档无权限：先确认是 CLI token 过期还是文档本身无权限；token 过期按上面的授权流程处理，文档无权限再让用户提供可访问文档或 Markdown；
- 文档链接失效：让用户更新链接；
- 文档只有截图：先识别截图中的字段和流程，无法确认的标未决；
- 文档内容互相矛盾：列出冲突，等待用户决策；
- 不允许为了继续写代码而编造需求。
