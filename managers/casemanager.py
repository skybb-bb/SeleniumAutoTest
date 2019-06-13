from case.reader.base import BaseReader
from case.reader.excel import ExcelReader
from exception.exception import NoPorterError, EmptyPackagesError
from util.packager.base import BasePackager
from util.packager.packager import ProcessPackager
from util.porter.BasePorter import BasePorter
from util.porter.porter import Porter


class CaseManager:
    """
    CaseManager主要负责porter和packager的调度(目前单线程)
    """

    def __init__(self):
        self.__porter = None
        self.__packager = set()
        self.__reader = set()

    def register_porter(self, porter):
        if isinstance(porter, BasePorter):
            self.__porter = porter
        else:
            self.exception(porter, "porter")

    def exception(self, exc, msg):
        raise ValueError("{0} is not {1}".format(exc.__class__, msg))

    def register_reader(self, reader):
        if isinstance(reader, BaseReader):
            self.__reader.add(reader)
        else:
            self.exception(reader, "reader")

    def register_packager(self, packager):
        if isinstance(packager, BasePackager):
            self.__packager.add(packager)
        else:
            self.exception(packager, "packager")

    def start(self):
        while True:
            try:
                if self.__porter is None:
                    raise NoPorterError("porter is none")
                # 从reader集合中获取一个reader
                reader = self.__reader.pop()
                # 从packager集合中获取一个packager
                packager = self.__packager.pop()
                # packager指定reader
                packager.select_reader(reader)
                # packager 打包
                packager.packing()
                # porter接受
                self.__porter.recv(packager.send())
            except ValueError:
                break

    def get_porter(self):
        if len(self.__porter) == 0:
            raise EmptyPackagesError("porter`s package is empty")
        if self.__porter:
            return self.__porter
        raise NoPorterError("porter is none")


if __name__ == '__main__':
    r = ExcelReader("/home/amdins/桌面/teach/seleniums/selenium/case.xlsx")
    man = CaseManager()
    man.register_reader(r)
    man.register_packager(ProcessPackager())
    man.register_porter(Porter())
    man.start()
    p = man.get_porter()
    print(len(p))