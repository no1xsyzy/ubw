from ._base import *

StickyKey = str


class ConsoleUI(BLiveUI):
    uic: Literal['console'] = 'console'
    verbose: int = 0
    datetime_format: str = '[%Y-%m-%d %H:%M:%S]'

    def format_record(self, record: Record) -> str:
        s = [rf"{record.time.strftime(self.datetime_format)} "]
        for seg in record.segments:
            match seg:
                case PlainText(text=text):
                    s[0] += text
                case Anchor(text=text, href=href):
                    s[0] += f"[{text}]({href})"
                case User(name=name, uid=uid):
                    s[0] += f"{name} ({uid=})"
                case Room(owner_name=on, room_id=room_id):
                    s[0] += f"{on}的直播间 ({room_id=})"
                case RoomTitle(title=title, room_id=room_id):
                    s[0] += f"《{title}》 ({room_id=})"
                case ColorSeeSee(text=text):
                    s[0] += text
                case DebugInfo(text=text, info=info):
                    if self.verbose > 0:
                        s[0] += f"[{text}...]"
                        s.append(f"[{text}]")
                        import json
                        js = json.dumps(info, ensure_ascii=False)
                        if len(js) > 80:
                            s.append(js)
                        else:
                            s.append(json.dumps(info, ensure_ascii=False, indent=2))
                    else:
                        s[0] += f"(info...)"
        return '\n'.join(s)

    def add_record(self, record: Record, sticky=False):
        print(self.format_record(record))

    def remove(self, key):
        pass

    def unstick(self, key):
        pass

    def unstick_before(self, key, before):
        pass


if __name__ == '__main__':
    demo(ConsoleUI(verbose=1))
