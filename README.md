# wiki_exporter
用于导出wiki文章为pdf
修改自 https://github.com/qquunn/batch-export-wiki-pdf.git

## 使用方式
1. 环境依赖：Python3
2. 安装需要的包
3. 修改以下配置
```python3 
cookieString = "JSESSIONID=xxxxxxx;"
wiki_page_url = "https://path/to/wiki/pages/viewpage.action?pageId=xxx"
wiki_title = "标题"
dir = "./"+wiki_title
```
4. 执行main
