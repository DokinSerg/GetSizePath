import os
import sys
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
__version__ = '0.0.3'
__verdate__ = '2025-04-18 08:54'
SourcePath = 'C:\\'
semaphore = asyncio.Semaphore(5000)
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
        rpn(']')
        rpn(f'Задержка по таймеру {slep_time}')
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
                    await asyncio.sleep(0.01)
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
        await asyncio.sleep(0.1)
    #--------------------------------------------------------
        for task in task_sa:
            counfile += task.result()[2]
            cursize += task.result()[1]
    #--------------------------------------------------------
    except PermissionError:
        pass
        # rpn(f'[khaki1]Отказано в доступе {CurPath}')
        # rpn(f'[khaki1]{CurPath}')
    except Exception as _err:
        rpn(f'[red1]PP:{_err}')
        rpn(f'[red1]PP:{traceback.format_exc()}')
    return CurPath,cursize,counfile
##############################################################################################################
async def main()-> None:
    global WaitPrBar
    DirSize:dict[str,int] = {}
    all_size = 0
    CountFiles = 0
    try:
        tasks = []
        rpn(f'Расчет объёма диреторий для {SourcePath}')
        start_Src = perf_counter()
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
        if not tsc.done():tsc.get_coro().close()
        await asyncio.sleep(0.01)
    #--------------------------------------------------------------------------------------
        sizekb = round(all_size/kGb,3)
        rpn()
        for i,j in DirSize.items():
            rpn(f'[turquoise2]{i:40} [green1]{round(j/kGb,3):10}')
        rpn(f'[turquoise2]Всего файлов [green1]{CountFiles} [turquoise2]общим размером [green1]{all_size} [turquoise2]байт ([green1]{sizekb} Mb)\n')
        stop_Src = perf_counter()
        FileListTime = round(stop_Src - start_Src,3)
        rpn(f'Составление списка файлов заняло {FileListTime}c')
    #--------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------
        # await asyncio.create_task(LogMessage(f'Копирование завершено. Скопировано {len(FileList)} файлов. Время копирования {copy_time} c'))
        # await asyncio.sleep(0.1)
    #-------------------------------------------------------------------------------------
    except Exception as err:
        rpn(f'[red1]Main:{err}')
        rpn(f'[red1]Main:{traceback.format_exc()}')
###############################################################################################################
start_time = perf_counter()
asyncio.run(main())
stop_time = perf_counter()
Inetrval = stop_time - start_time
print(f'\nОбщее время выполнения {Inetrval:.7f}')
if not (len(sys.argv) > 1 and sys.argv[1] == 'cons'):input(':-> ')
os._exit(0)
