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
    programs = dom.getElementsByTagName('programme')
    
    master = {}
    for program in programs:
        channel = program.attributes['channel'].value
        channel = channel.split('.')[0]
        if channel not in master:
            master[channel] = []
        start = program.attributes['start'].value
        start = datetime.datetime.strptime(start, '%Y%m%d%H%M%S %z')
        stop = program.attributes['stop'].value
        stop = datetime.datetime.strptime(stop, '%Y%m%d%H%M%S %z')
        title_tag = program.getElementsByTagName('title')
        title = title_tag[0].firstChild.data if title_tag.length > 0 else ''
        desc_tag = program.getElementsByTagName('desc')
        description = desc_tag[0].attributes['desc'].value if desc_tag.length > 0 else ''
        img_tag = program.getElementsByTagName('icon')
        img_url = img_tag[0].attributes['src'].value if img_tag.length > 0 else ''

        # program_status
        # 1 => upcoming; 0 => now playing; -1 => finished
        program_status = 1
        if now > stop:
            program_status = -1
        elif now >= start and now < stop:
            program_status = 0
        
        master[channel].append({
                'start': datetime.datetime.strftime(start, '%Y-%m-%d %I:%M%p %z'),
                'stop': datetime.datetime.strftime(stop, '%Y-%m-%d %I:%M%p %z'),
                'title': title.encode('ascii', 'replace').decode('ascii'),
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

        # Writing now-and-next programs details
        with open(f'{channel}/current_and_upcoming.txt', 'w') as writer:
            writer.write(f'{now_and_upcoming}')
        
    
