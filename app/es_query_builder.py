class ESQueryBuilder:

    def __init__(self):
        self.bool_query = {
            "bool": dict()
        }
        self.es_query = {'query': self.bool_query}

    def collapse_field(self, field):
        self.es_query.update({'collapse': {'field': field}})

    def required_fields(self, field_list):
        self.es_query.update({'_source': field_list})

    @staticmethod
    def exists_field(field):
        return {
            'exists': {'field': field}
        }

    @staticmethod
    def term_query(field, value) -> dict:
        return {
            "match": {
                field: value
            }
        }

    @staticmethod
    def wildcard_query(field, value) -> dict:
        return {
            'wildcard': {
                field: value
            }
        }

    @staticmethod
    def multi_match(field_list, value) -> dict:
        return {
            'multi_match': {
                'query': value,
                'fields': field_list
            }
        }

    @staticmethod
    def match_phrase(field, value) -> dict:
        return {
            "match_phrase": {
                field: value
            }
        }

    def must(self, obj):
        if not isinstance(self.bool_query.get('bool').get('must'), list):
            self.bool_query.get('bool').update({'must': list()})
        self.bool_query.get('bool')['must'].append(obj)

    def must_not(self, obj):
        if not isinstance(self.bool_query.get('bool').get('must_not'), list):
            self.bool_query.get('bool').update({'must_not': list()})
        self.bool_query.get('bool')['must_not'].append(obj)

    def should(self, obj):
        if not isinstance(self.bool_query.get('bool').get('should'), list):
            self.bool_query.get('bool').update({'should': list()})
        self.bool_query.get('bool')['should'].append(obj)

    def should_not(self, obj):
        if not isinstance(self.bool_query.get('bool').get('should_not'), list):
            self.bool_query.get('bool').update({'should_not': list()})
        self.bool_query.get('bool')['should_not'].append(obj)

    def es_filter(self, obj):
        if not isinstance(self.bool_query.get('bool').get('filter'), list):
            self.bool_query.get('bool').update({'filter': list()})
        self.bool_query.get('bool')['filter'].append(obj)

    @staticmethod
    def prefix_query(field, prefix) -> dict:
        return {
            'prefix': {
                field: prefix
            }
        }

    @staticmethod
    def range_query(field, min_val=None, max_val=None, range_doc=None) -> dict:
        if range_doc:
            return {
                "range": {
                    field: range_doc
                }
            }

        if not max_val:
            return {
                "range": {
                    field: {
                        'gte': min_val
                    }
                }
            }

        if not min_val:
            return {
                "range": {
                    field: {
                        "lt": max_val
                    }
                }
            }

        return {
            "range": {
                field: {
                    "from": min_val,
                    "to": max_val
                }
            }
        }

    @staticmethod
    def terms_query(field, value_list) -> dict:
        return {
            "terms": {
                field: value_list
            }
        }

    @staticmethod
    def distinct_field_count_query(field: str) -> dict:
        return {
            "aggs": {
                "type_count": {
                    "cardinality": {
                        "field": field
                    }
                }
            }
        }

    @staticmethod
    def distinct_field_query(field: str) -> dict:
        return {
            "aggs": {
                "distinct_field": {
                    "terms": {
                        "field": field,
                        "size": 100
                    }
                }
            }
        }

    @staticmethod
    def nested_match_query(path, field=None, value_list=list(), bool_obj=None) -> dict:
        if not bool_obj:
            bool_obj = ESQueryBuilder()
            for value in value_list:
                bool_obj.should(ESQueryBuilder.term_query(field, value))
        return {
            'nested': {
                'path': path,
                'query': bool_obj
            }
        }

    def get_query(self) -> dict:
        return self.bool_query

    def parse_object_to_json(self, query_obj) -> (dict, list):
        if isinstance(query_obj, dict):
            if len(query_obj.values()) == 1 and isinstance(query_obj.values(), (str, int)):
                return query_obj
            for key, val in query_obj.items():
                query_obj[key] = self.parse_object_to_json(val)
            return query_obj
        if isinstance(query_obj, list):
            for index, item in enumerate(query_obj):
                query_obj[index] = self.parse_object_to_json(item)
            return query_obj
        if isinstance(query_obj, ESQueryBuilder):
            return self.parse_object_to_json(query_obj.get_query())
        if isinstance(query_obj, (int, str)):
            return query_obj

    @staticmethod
    def term_keyword_query(field, value) -> dict:
        return {
            "term": {
                '{}.keyword'.format(field): value
            }
        }
    
    @staticmethod
    def _add_instock_to_query(bool_query, inventory_id=None):
        if inventory_id:
            bool_query.must(ESQueryBuilder.range_query('inventory_details.{}'.format(inventory_id), range_doc={'gt': 0}))
