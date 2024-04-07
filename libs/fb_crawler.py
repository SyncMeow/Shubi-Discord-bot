#from libs.settings import fb_login_data
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import asyncio

#https://www.facebook.com/people/%E9%BB%91%E8%89%B2%E9%BA%BB%E4%B8%AD20/100077423478931/
#jikcssrz  the tag of the posts

class FB_crawler():
  def __init__(self) -> None:
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    self.driver = webdriver.Chrome("./libs/chromedriver/chromedriver",chrome_options=chrome_options)
    self.post_history = []

  async def webdriver_login(self):
    self.driver.get("http://www.facebook.com")
    await asyncio.sleep(3)	
    self.driver.find_element_by_id("email").send_keys("email")
    self.driver.find_element_by_id("pass").send_keys("password") 
    self.driver.find_element_by_name("login").click()
    await asyncio.sleep(3)
  
  async def click_more(self, text):
    for i in range(3):
      comment_more = self.driver.find_element(By.PARTIAL_LINK_TEXT, text)
      if len(comment_more) == 0:
        break
      for btn in comment_more:
        try:
          btn.click()
          await asyncio.sleep(1)
          print('. ',end='')
        except:
          continue

  async def find_number(self, root) -> str:
    numbers = root.find_all("a", class_ = "qi72231t nu7423ey n3hqoq4p r86q59rh b3qcqh3k fq87ekyn bdao358l fsf7x5fv rse6dlih s5oniofx m8h3af8h l7ghb35v kjdc1dyq kmwttqpk srn514ro oxkhqvkx rl78xhln nch0832m cr00lzj9 rn8ck1ys s3jn8y49 icdlwmnq cxfqmxzd d1w2l3lo tes86rjd")
    number = numbers[0].text if len(numbers) else "0"
    return number
  
  async def find_text(self, root) -> str:
    sentences = root.find_all("div", dir = "auto")
    content = ""
    if len(sentences):
      for sentence in sentences:
        content += sentence.text + "\n"
    return content

  async def find_images(self, root) -> list[str]:
    images = root.find_all(
    "img", class_=["z6erz7xo on4d8346 pytsy3co s8sjc6am myo4itp8 ekq1a7f9 mfclru0v p9wrh9lq"])
    imgs_source = []
    if len(images):
      for img in images:
        imgs_source.append(img["src"])
    return imgs_source       

  async def getpage(self):
    self.driver.get("https://www.facebook.com/people/%E9%BB%91%E8%89%B2%E9%BA%BB%E4%B8%AD20/100077423478931/")
    data = {}
    for i in range(50):
      soup = BeautifulSoup(self.driver.page_source, "html.parser")
      roots = soup.find_all(
    "span", class_="gvxzyvdx aeinzg81 t7p7dqev gh25dzvf exr7barw b6ax4al1 gem102v4 ncib64c9 mrvwc6qr sx8pxkcf f597kf1v cpcgwwas m2nijcs8 hxfwr5lz k1z55t6l oog5qr5w tes86rjd pbevjfx6 ztn2w49o")
      for root in roots:
        number = await self.find_number(root)
        content = await self.find_text(root)
        imgs = await self.find_images(root)
        if number in self.post_history: 
          continue
        else: 
          data[number] = (content, imgs)
          self.post_history.append(number)
          self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
      await asyncio.sleep(2)
    return data

fb_crawler = FB_crawler()
data = asyncio.run(fb_crawler.getpage())
w = open("./record.txt","w", encoding='utf-8')
for key, value in data.items():
  w.write(f"{key}\n{value[0]}\n{value[1]}\n")
  print(f"{key}\n{value[0]}\n{value[1]}\n")
w.close()
