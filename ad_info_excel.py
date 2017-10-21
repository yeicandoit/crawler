# -*- coding: utf-8 -*-

import time
import requests
import csv

urlDemand = "https://mp.weixin.qq.com/promotion/snsdelivery/sns_advert_mgr?page=%d&page_size=100&action=list&status=0&begin_time=1492876800&end_time=1523980800&list_type=2&token=3219569498&appid=&spid=&_=1508501460795"
urlAdinfo = "https://mp.weixin.qq.com/promotion/snsdelivery/snsstat?action=get_detail&cid=%d&token=3219569498&appid=&spid=&_=1508501658507"
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Cookie': 'pgv_pvi=3558392832; pgv_si=s9755152384; mmad_session=8575930063d0816b67fb614bc0978c707d8097147abf51c6bcde4a9163cd3addb8e91c921d953e1161372cb8a1cf8d77e39bc6b662f7480417cc387a3a127ce8c65347c1d0527d4f41575514fd624360de5e0093430dcb7f50b87eb0ff0f116f901d4b8f554b4b2bfd8b65a6ea275447dbe712cd45aa70e68393478df02b17aec0754b4ccbdaf630524cc87223ac91b5; data_bizuin=3270617616; data_ticket=ygvrlEKsAsuRmiQhW44gsczFI+r6Gh2VX5vOuc4csMKaojDMTFqhoHYqacz56S1F; sp_login_mark=150850140645042; pgv_info=ssid=s4711913930; ts_last=mp.weixin.qq.com/promotion/frame; pgv_pvid=2689713886; ts_uid=1476663110',
    'Host': 'mp.weixin.qq.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

statusMap = {
    5 : u'待投放'.encode('GB2312'),
    6 : u'投放中'.encode('GB2312'),
    7 : u'投放结束'.encode('GB2312'),
    8 : u'暂停投放'.encode('GB2312'),
    9 : u'未通过'.encode('GB2312'),
    10001 : u'创建中'.encode('GB2312'),
}

def getAds():
    with open("test.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([u"广告名称".encode('GB2312'), u"投放状态".encode('GB2312'), u"投放时间".encode('GB2312'),
                         u"总曝光(次)".encode('GB2312'), u"总花费(元)".encode('GB2312'), u"详情查看量(次)".encode('GB2312'),
                         u"门店查看量".encode('GB2312'), u"图片点击量".encode('GB2312'), u"点赞评论量".encode('GB2312'),
                         u"关注量".encode('GB2312'), u"转发量".encode('GB2312')])

        page = 1
        while 1:
            url = urlDemand % (page)
            r = requests.get(url, headers=headers)
            rJson = r.json()
            if page > rJson['conf']['total_page']:
                break
            page += 1

            if 0 == rJson['base_resp']['ret']:
                ads = rJson['list']
            else:
                ads = []
            for row in ads:
                try:
                    name = row['campaign']['cname'].encode('GB2312')
                except:
                    print "%s could not transfer to GB2312" % (row['campaign']['cname'])
                    name = row['campaign']['cname'].encode('utf-8')
                try:
                    status = statusMap[row['campaign']['real_status']]
                except:
                    print "%s has unexpected real_status:%d" %(name, row['campaign']['real_status'])
                    status = u'未知'.encode('GB2312')
                begin_time = time.localtime(row['campaign']['begin_time'])
                end_time = time.localtime(row['campaign']['end_time'])
                date_range = u"%d年%d月%d日-%d年%d月%d日" %(begin_time.tm_year, begin_time.tm_mon, begin_time.tm_mday,
                                                     end_time.tm_year, end_time.tm_mon, end_time.tm_mday)
                date_range = date_range.encode('GB2312')

                #Get ad detail info
                url = urlAdinfo % (row['campaign']['cid'])
                r = requests.get(url, headers=headers)
                rJson = r.json()
                if 0 == rJson['base_resp']['ret']:
                    try:
                        adInfo = rJson['detail']
                        view_count = adInfo['view_count']
                        total_cost = float(adInfo['total_cost']) / 100
                        click_url_count = adInfo['click_url_count']
                        poi_pv = adInfo['poi_pv']
                        click_pic_count = adInfo['click_pic_count']
                        heart_comment_count = adInfo['heart_count'] + adInfo['comment_count']
                        click_follow_count = adInfo['click_follow_count']
                        share_friend_action_count = adInfo['share_friend_action_count']
                        writer.writerow([name, status, date_range, view_count, total_cost, click_url_count, poi_pv,
                                         click_pic_count, heart_comment_count, click_follow_count, share_friend_action_count])
                    except:
                        writer.writerow([name, status, date_range])
                        print "%d %s view_count error" % (row['campaign']['cid'], name)
                else:
                    print "%d %s has no ad detail info" % (row['campaign']['cid'], name)
                    writer.writerow([name, status, date_range])

if __name__ == '__main__':
    getAds()

