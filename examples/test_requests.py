#%%

import requests

# r = requests.get('http://docs.python-requests.org/en/master/user/quickstart/#make-a-request')
r = requests.get('https://rg.ru/2019/02/27/mid-rf-moskva-obespokoena-krizisom-mezhdu-indiej-i-pakistanom.html')

print(r.text)

r.close()




#%% this is a new cell

from requests_html import HTMLSession

session = HTMLSession()
# r = session.get('http://docs.python-requests.org/en/master/user/quickstart/#make-a-request')
# r = session.get('https://www.calhoun.io/')
r = session.get('https://rg.ru/2019/02/27/mid-rf-moskva-obespokoena-krizisom-mezhdu-indiej-i-pakistanom.html')
print(r.html.text)


for link in r.html.absolute_links:
    print(link)

r.close()



#%%
