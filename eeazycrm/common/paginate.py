from flask import request
import math


class Paginate:
    def __init__(self, query, page=1, per_page=10):
        self.page = request.args.get('page', page, type=int)
        self.per_page = request.args.get('per_page', per_page, type=int)

        if self.per_page < 10:
            self.per_page = 10

        self.total_records = query.count()
        self.pages = int(math.ceil(self.total_records / self.per_page))

        if self.page < 1:
            self.page = 1
        elif self.page > self.pages > 0:
            self.page = self.pages

        self.current_page = self.page
        self.query = query

    def items(self):
        offset = (self.page - 1) * self.per_page
        return self.query.offset(offset).limit(self.per_page).all()

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        if self.total_records < self.per_page:
            return False
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

