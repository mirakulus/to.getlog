
class FileExplorer():
    ''' Построчное чтение файлов. Возможно обращение к произвольной строке. 
    Если строка уже была прочитана/итерирована, то переход к ней будет осуществляться быстро,
    т.к. информация об офсетах строк кешируется '''

    def __init__(self, file_object_open_method, file_path, open_mode):
        ''' 
        file_object_open_method - метод, который создает file-like объект
        file_path - путь к файлу
        open_mode - метод открытия (r, w, rb, a и так далее). 
                    От метода открытия зависит тип возвращаемых строк.
                    Например, при открытии в режиме rb, будет возвращена строка в виде массива байт'''
        self._file_open_method = file_object_open_method
        self._open_mode = open_mode
        self.file_path = file_path
        self._file = self._file_open_method(self.file_path, self._open_mode)
        self._file_enum = enumerate(self._file)
        self._line_offsets = [ ]
        self._cur_offset = 0
        self._cur_line_index = 0

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        return self
    def __next__(self):
        line_index, line = self._file_enum.__next__()
        self._line_offsets.append(self._cur_offset)
        self._cur_offset += len(line)
        self._cur_line_index = line_index + 1
        return line

    def _seek_offset(self, offset):
        ''' устанавливает курсор на указанную позицию в файле '''
        self._cur_offset = offset
        return self._file.seek(offset, 0)


    @property
    def cur_line_index(self):
        ''' номер строки в начале которой стоит курсор (0-based) '''
        return self._cur_line_index

    @property
    def cur_offset(self):
        ''' текущий оффсет с начала файла на котором стоит курсор '''
        return self._cur_offset


    def seek(self, line_index):
        ''' устанавилвает курсор на начало указанную строку. 
        Если файл уже читался и оффсет строки закеширован чтение файла заново не происходит '''
        if len(self._line_offsets) > line_index:
            self._seek_offset(self._line_offsets[line_index])
        else:
            for i in range(len(self._line_offsets), line_index):
                self.__next__()

    def read(self, lines_amount=1, start_pos=-1):
        ''' построчно читает файл, начиная с указанной позиции. Возвращает прочитанные строки
        lines_amount - количество строк, которое нужно прочесть. Если < 0, Будет проитана одна строка
        start_pos - позиция в файле откуда начинать чтение. По умолчанию (-1) - начинает с текущей позиции
        return - если прочитана одна строка - вернет строку. Если более - вернет массив строк '''
        if lines_amount < 0:
            lines_amount = 1

        if start_pos != -1:
            raise NotImplementedError

        if lines_amount == 1:
            return self.__next__()
        else:
            start_pos = self.cur_line_index
            end_pos = start_pos + lines_amount
            lines = []
            while self.cur_line_index < end_pos:
                lines.append(self.__next__())

            return lines

    def search_for(self, string):
        ''' Поиск вхождения указанной строки в файле и остановка курсора на линии с ней.
        returns boolean - найдено ли вхождение или нет  '''
        bstring = string.encode(self.encoding)
        for l in self.read():
            if bstring in l:
                return True
        return False
    
    def close(self):
        self._file.close()