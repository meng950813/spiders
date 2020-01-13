"""
学科评估结果爬虫
"""
#-*- coding:utf-8 -*-
import requests,json
from lxml import etree

class SubjectEvaluation(object):
  # 基础url
  base_url = "https://www.cdgdc.edu.cn/webrms/pages/Ranking/"
  # 起始url
  start_url = "https://www.cdgdc.edu.cn/webrms/pages/Ranking/xkpmGXZJ2016.jsp?xkdm="
  # 学科大类参数
  parms = {"人文社科类": "01,02,03,04,05,06", 
    "理学": "07",
    "工学": "08",
    "农学": "09",
    "医学": "10",
    "管理学": "12",
    "艺术学": "13"
  }

  headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Cookie": "scrolls=0; JSESSIONID=DE9534D45ED84E8CE3FB1802D12E5D83; sto-id-20480-xww_webrms=CBAKBAKMEJBP; UM_distinctid=169e6a07d95878-06941f069027ed-7a1437-1fa400-169e6a07d979d9; sto-id-20480-web_80=CBAKBAKMJABP; bdshare_firstime=1554352665228; sto-id-47873-web_80=CCAKBAKMJABP; sto-id-47873-xww_webrms=CCAKBAKMEJBP; CNZZDATA2328862=cnzz_eid%3D22254684-1554351939-null%26ntime%3D1557836402",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
  }

  FILE = ""

  def __init__(self):
    self.FILE = open("学科评估.json", "w", encoding="utf-8")

  def close(self):
    self.FILE.close()

  def start(self):
    """
    开始爬虫，将网页结果写入本地
    """
    for key, value in self.parms.items():
      # print(key,value)
      # print("url : ", (self.start_url+value))
      response = requests.request("get",self.start_url+value, headers= self.headers)
      response.encoding = "gb2312"
      # print(response.text)
      
      back_data = self.parse(response)
      
      self.FILE.write(json.dumps(back_data, ensure_ascii=False))

  def parse(self, response):
    """
    解析学科大类的数据, 如 理学/ 工学
    return: {
      "0101": {
        "sub_name" : "哲学",
        "result" : {
          "A+" : ["xx大学","cxxx",....],
          "A" : ["xx大学","cxxx",....],
        },
      "0201":{
        "sub_name" : "理论经济学",
        "result" :{....}
      } 
    } 
    """
    tree = etree.HTML(response.text)

    return_data = {}
    # 获取二级学科链接
    links = tree.xpath("//div[@id='leftgundong']//table//p//a/@href")
    for i in range(0,len(links)):
      href = self.base_url + links[i]

      res = requests.get(href, headers=self.headers)
      res.encoding = "gb2312"
      return_data.update( self.analysisContent(res.text) )

    return return_data

 
  def analysisContent(self, content, fromFile=False):
    """
    return {"0101": {
        "sub_name" : "哲学",
        "result" : {
          "A+" : ["xx大学","cxxx",....],
          "A" : ["xx大学","cxxx",....],
        }
      }
    """

    # 10674&nbsp;&nbsp;&nbsp;&nbsp;昆明理工大学 => 10674……昆明理工大学
    content = content.\
      replace("&nbsp;&nbsp;&nbsp;&nbsp;","……").\
      replace("&nbsp;","")
    
    tree = etree.HTML(content)
    title = tree.xpath("//table//p//strong/text()")[0]
    
    if not fromFile:
      fileName = "source/%s.html" % title.replace(" ","_")
      with open(fileName, "wb") as f:
        f.write(content.encode("utf-8"))
    
    result_container = tree.xpath("//table")[-1]
    # print(result_container)
    trs = result_container.xpath("./tr")
    # print(len(trs))

    title = title.split("  ")
    return_data = {str(title[0]):{
      "sub_name" : str(title[1]),
      "result":{}
    }}

    data = return_data[str(title[0])]['result']
    tag = ""
    for tr in trs:
      tds = tr.xpath(".//td//text()")
      # print(tr.xpath(".//td"))
      print(tds)
      # 新评级
      if len(tds) > 1:
        # tds = ["A+"","10674……昆明理工大学"]
        tag = tds[0].strip()
        data[tag] = [tds[1].strip().split("……")[-1]]
      elif len(tds) == 1:
        # tds = ["10674……昆明理工大学"]
        data[tag].append(tds[0].strip().split("……")[-1])
      else:
        print("something error")

    return return_data


  def run(self):
    # self.start()
    # self.close()

    self.readFromDisk()


  def readFromDisk(self):
    """
    读取保存的网页内容
    """
    import os
    path = "./source" #文件夹目录
    files= os.listdir(path) #得到文件夹下的所有文件名称
    print(files)
    data = {}
    for file in files: #遍历文件夹
      f = open(path+"/"+file, "rb") #打开文件
      back = self.analysisContent(f.read().decode("utf-8"))
      data.update(back)
    
    with open("学科评估.json", "w") as f:
      f.write(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
  obj = SubjectEvaluation()
  obj.run()