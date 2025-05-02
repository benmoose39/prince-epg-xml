from xml.dom import minidom
import requests
import json
import os
import datetime
import sys


if __name__ == '__main__':
    s = requests.session()
    
    now = datetime.datetime.now(datetime.UTC)
    dom = minidom.parse('IPTV_tuner_epg.xml')
    channels = dom.getElementsByTagName('channel')
    programs = dom.getElementsByTagName('programme')

    channel_dict = {}
    for channel in channels:
        key = channel.attributes['id'].value.split('.')[0]
        value_tag = channel.getElementsByTagName('display-name')
        value = value_tag[0].firstChild.data if value_tag.length > 0 else ''
        channel_dict[key] = value
    
    master = {}
    for program in programs:
        channel = program.attributes['channel'].value
        channel = channel.split('.')[0]
        channel_name = channel_dict.get(channel, channel)
        if channel not in master:
            master[channel] = []
        start = program.attributes['start'].value
        start = datetime.datetime.strptime(start, '%Y%m%d%H%M%S %z')
        stop = program.attributes['stop'].value
        stop = datetime.datetime.strptime(stop, '%Y%m%d%H%M%S %z')
        title_tag = program.getElementsByTagName('title')
        title = title_tag[0].firstChild.data if title_tag.length > 0 else ''
        sub_title_tag = program.getElementsByTagName('sub-title')
        sub_title = sub_title_tag[0].firstChild.data if sub_title_tag.length > 0 else ''
        desc_tag = program.getElementsByTagName('desc')
        description = desc_tag[0].attributes['desc'].value if desc_tag.length > 0 else ''
        img_tag = program.getElementsByTagName('icon')
        img_url = img_tag[0].attributes['src'].value if img_tag.length > 0 else 'https://commons.wikimedia.org/wiki/File:Image_not_available.png'

        # program_status
        # 1 => upcoming; 0 => now playing; -1 => finished
        program_status = 1
        if now > stop:
            program_status = -1
        elif now >= start and now < stop:
            program_status = 0
        
        master[channel].append({
                'channel_name': channel_name,
                'start_time': datetime.datetime.strftime(start, '%d %B %Y %I:%M%p %Z'),
                'start': datetime.datetime.strftime(start, '%I:%M%p'),
                'start_date': datetime.datetime.strftime(start, '%d %B %Y'),
                'stop_time': datetime.datetime.strftime(stop, '%d %B %Y %I:%M%p %Z'),
                'stop': datetime.datetime.strftime(stop, '%I:%M%p'),
                'title': title.encode('ascii', 'replace').decode('ascii'),
                'sub_title': sub_title.encode('ascii', 'replace').decode('ascii'),
                'description': description.encode('ascii', 'replace').decode('ascii'),
                'img_url': img_url,
                'program_status': program_status,
            })

    if 'files' not in os.listdir():
        os.mkdir('files')
    os.chdir('files')

    count = 0
    total_channels = len(master)
    for channel in master:
        count += 1
        print(f'[+] Getting tv guide for {channel}... [{count}/{total_channels}]')
        # Create folder if not already present
        if channel not in os.listdir():
            try:
                os.mkdir(channel)
            except FileExistsError:
                continue

        # creating xml
        doc = minidom.Document()
        root = doc.createElement("tv")
        doc.appendChild(root)

        '''
        now_and_upcoming = ''
        for program in master[channel]:
            if program['program_status'] == -1:
                continue
            if program['program_status'] == 0:
                # Writing current program details
                with open(f'{channel}/current_program.txt', 'w') as writer:
                    writer.write(f'{program["start"]}\n{program["title"]}\n{program["description"]}')

                # Writing current program title
                with open(f'{channel}/current_program_title.txt', 'w') as writer:
                    writer.write(f'{program["title"]}')

                # Writing current program image link
                with open(f'{channel}/current_program_image.txt', 'w') as writer:
                    writer.write(f'{program["img_url"]}')
                if program['img_url']:
                    img_response = s.get(program['img_url'])
                    with open(f'{channel}/current_program_image.jpg', 'wb') as file:
                        file.write(img_response.content)

            now_and_upcoming += f'{program["start"]}\n{program["title"]}\n{program["description"]}\n\n'
        '''
        
        for program in master[channel]:
            if program['program_status'] == -1:
                continue
            if program['program_status'] in [0,1]:
                ch = doc.createElement("channel")
                root.appendChild(ch)
                
                ch_name = doc.createElement('name')
                ch_name_text = doc.createTextNode(f'{program["channel_name"]}')
                ch_name.appendChild(ch_name_text)
                ch.appendChild(ch_name)

                title = doc.createElement('title')
                title_text = doc.createTextNode(f'{program["title"]}')
                title.appendChild(title_text)
                ch.appendChild(title)

                desc = doc.createElement('desc')
                desc_text = doc.createTextNode(f'{program["description"]}')
                desc.appendChild(desc_text)
                ch.appendChild(desc)

                image = doc.createElement('image')
                image_url = doc.createTextNode(f'{program["img_url"]}')
                image.appendChild(image_url)
                ch.appendChild(image)

                start = doc.createElement('start')
                start_time = doc.createTextNode(f'{program["start"]}')
                start.appendChild(start_time)
                ch.appendChild(start)

                finish = doc.createElement('finish')
                finish_time = doc.createTextNode(f'{program["stop"]}')
                finish.appendChild(finish_time)
                ch.appendChild(finish)

                date = doc.createElement('date')
                date_text = doc.createTextNode(f'{program["start_date"]}')
                date.appendChild(date_text)
                ch.appendChild(date)

        # Writing now-and-next programs details
        # with open(f'{channel}/current_and_upcoming.txt', 'w') as writer:
        #     writer.write(f'{now_and_upcoming}')

        xml_str = doc.toprettyxml(indent='  ')
        
        with open (f'{channel}/epg.xml', 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
    
