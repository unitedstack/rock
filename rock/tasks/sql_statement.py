# -*- coding: utf-8 -*-


def get_last(table):
    return "select * from %s order by updated_at desc limit 1" % table
