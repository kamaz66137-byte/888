# AGENTS
- must 为必须遵守的规则,绝对不可有任何违背!!
- 全局必须使用UTF-8编码,禁止使用任何非UTF-8编码的文件或内容
- 绝不能用 Get-Content / Set-Content（除非明确加 -Encoding UTF8，但那会写入带 BOM 的文件）。


## instructions 指令动作

|    instructions    |                             must                             |
| :----------------: | :----------------------------------------------------------: |
|      测试xxx       | 必须实际真实测试,不能凭空想象,必须实质性的全部跑一遍,并发现其中的问题/bug/是否兼容/等系列问题,并保存为md文件,作为交付物的一部分 |
| 创建技能/创建skill |            必须上下文要清晰,必须知道该技能是功能, 作用,并使用.github/skills/AGENTS.md 及  .github/skills/skills-skills/SKILL.md 来创建技能         |
|                    |                                                              |

