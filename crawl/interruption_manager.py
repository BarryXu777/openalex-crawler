import signal

received_interrupt = False


def interrupted():
    return received_interrupt


def cancel_interrupt():
    global received_interrupt
    received_interrupt = False


def set_interrupt():
    global received_interrupt
    received_interrupt = True


def interrupt_handler(signal, frame):
    print(f"[interruption manager] 收到中断信号{'SIGINT' if signal == 2 else 'SIGTERM'}，程序将在当前任务完成后退出")
    set_interrupt()


signal.signal(signal.SIGINT, interrupt_handler)
signal.signal(signal.SIGTERM, interrupt_handler)
