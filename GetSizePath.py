import os
# import sys
# import uuid
import traceback
import asyncio
# import aiofiles
import aiofiles.os as aos
# from datetime import datetime,timezone,timedelta
from time import perf_counter
# from aioshutil import copy2 as Acopy2
from rich import print as rpn
#------------------------------------------
__author__ = 't.me/dokin_sergey'
__version__ = '0.0.6'
__verdate__ = '2025-04-24 20:03'
# SourcePath = r'c:\Users\dokin\AppData\Local\Yandex\YandexBrowser\User Data\Default'
semaphore = asyncio.Semaphore(7000)
WaitPrBar = True#ProgressBar Stop
kGb = 1048576

###############################################################################################################
async def ProgressBar()-> None:
    i=0
    Delay = 1
    # Step = 10
    start_PrBr = perf_counter()
    # rpn('[',end = '')
    try:
        while WaitPrBar:
            await asyncio.sleep(Delay)
            # if   not i % Step:rpn(f'{int(i*Delay):0>3d}',end = '')
            if not i:rpn('[',end = '')
            elif not i % 60:rpn(f'[cyan1] {i:4}')
            elif not i % 2:rpn('[green1]+',end = '')
            else:rpn('[green1]-',end = '')
            i += 1
    finally:
        stop_PrBr = perf_counter()
        slep_time = round(stop_PrBr - start_PrBr,3)
        rpn(f'] по таймеру {slep_time}')
        # rpn(f'Задержка по таймеру {slep_time}')
##############################################################################################################

################################################################################################################
async def ParsingPath_A(CurPath:str)->tuple[str, int, int]:
    cursize = 0
    counfile = 0
    try:
        async with semaphore:
            # rpn(f'[cyan1]{CurPath}')
            task_sa = []
            with await aos.scandir(CurPath) as itPaths:
                for item in itPaths:
                    await asyncio.sleep(0)
                    if item.is_dir(follow_symlinks=False):
                        # nextpaths.append(item.path)
                        task_a = asyncio.create_task(ParsingPath_A(item.path))
                        task_sa.append(task_a)
                        await asyncio.sleep(0.01)
                        continue
                    if item.is_file(follow_symlinks=False):
                        counfile += 1
                        cursize += item.stat().st_size
        #--------------------------------------------------------
        await asyncio.gather(*task_sa)
        await asyncio.sleep(0)
    #--------------------------------------------------------
        for task in task_sa:
            counfile += task.result()[2]
            cursize += task.result()[1]
    #--------------------------------------------------------
    except PermissionError:
        await asyncio.sleep(0)
        # rpn(f'[khaki1]Отказано в доступе {CurPath}')
        # rpn(f'[khaki1]{CurPath}')
    except Exception as _err:
        rpn(f'[red1]PP:{_err}')
        rpn(f'[red1]PP:{traceback.format_exc()}')
    return CurPath,cursize,counfile
##############################################################################################################
async def main(SourcePath:str)-> None:
    global WaitPrBar
    #-----------------------------------------------------------------------------
    while True:
        DirSize:dict[str,int] = {}
        all_size = 0
        CountFiles = 0
        # start_Src = perf_counter()
        try:
            tasks = []
            rpn(f'Расчет объёма диреторий для {SourcePath}')
            WaitPrBar = True
            tsc = asyncio.create_task(ProgressBar(),name='ProgressBar')
            with await aos.scandir(SourcePath) as itPaths:
                for item in itPaths:
                    await asyncio.sleep(0.01)
                    if item.is_dir(follow_symlinks=False):
                        task = asyncio.create_task(ParsingPath_A(item.path))
                        await asyncio.sleep(0)
                        tasks.append(task)
                        continue
                    if item.is_file(follow_symlinks=False):
                        CountFiles += 1
                        all_size += item.stat().st_size
        #--------------------------------------------------------------------------------------
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)
            # #--------------------------------------------------------------------------------
            for task in tasks:
                CountFiles += task.result()[2]
                all_size += task.result()[1]
                DirSize[task.result()[0]]  = task.result()[1]
        #--------------------------------------------------------------------------------------
            WaitPrBar = False
            await tsc
            if not tsc.done():
                tsc.get_coro().close()
            await asyncio.sleep(0.01)
        #--------------------------------------------------------------------------------------
        except Exception as err:
            rpn(f'[red1]Main:{err}')
            rpn(f'[red1]Main:{traceback.format_exc()}')
        #------------------------------------------------------------------------------------------
        sizekb = round(all_size/kGb,3)
        rpn()
        rpn(f'[green1]{SourcePath}\n')
        sortDirSize = dict(sorted(DirSize.items(),key=lambda itm: itm[1],reverse=True))
        Strlen = 30
        for i,j in enumerate(sortDirSize.items(),start = 1):
            ipath = os.path.basename(j[0])
            fsn = f'{ipath[:Strlen]} [khaki1]~' if len(ipath) > Strlen else ipath
            rpn(f'[green1]{i:3} [cyan1]{fsn:32} [green1]{j[1]/kGb:12_.3f}')
        rpn(f'\n[cyan1]Всего файлов [khaki1]{CountFiles:_} [cyan1]общим размером [khaki1]{all_size:_} [cyan1]байт ([khaki1]{sizekb:_} Mb)\n')
        # stop_Src = perf_counter()
        # FileListTime = round(stop_Src - start_Src,3)
        # rpn(f'Составление списка файлов заняло {FileListTime}c')
        rpn()
        #--------------------------------------------------------------------------------------
        while True:
            rpn('[cyan1]Введите номер папки. "0" возврат на уровень ввех')
            if not (kye := input('ENTER выход:-)> ')):return
            if kye =='0':
                SourcePath = os.path.dirname(SourcePath)
                break
            if kye.isdigit() and int(kye) <= len(sortDirSize):
                curDir = list(enumerate(sortDirSize))[int(kye)-1][1]
                SourcePath = os.path.join(SourcePath,curDir)
                rpn(SourcePath)
                break
        rpn('-'*100)
    #-------------------------------------------------------------------------------------
###############################################################################################################
start_time = perf_counter()
StartPath = 'C:\\'
rpn(f'[cyan1]Введите букву диска или [ [green1]{StartPath} [cyan1]]')
if not (key := input(' :-)> ')):
    key = StartPath
if key =='0':os._exit(0)
dr,_ = os.path.splitdrive(key)
if not dr: key = f'{key}:\\'
elif dr == StartPath:key = f'{key}\\'
asyncio.run(main(key))
input(':-> ')
os._exit(0)
