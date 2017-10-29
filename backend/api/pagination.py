from rest_framework.pagination import LimitOffsetPagination, _get_count, _positive_int


class Pagination(LimitOffsetPagination):
    # return all items if limit == 0
    def paginate_queryset(self, queryset, request, view=None):
        self.count = _get_count(queryset)
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        if self.limit == 0:
            self.limit = max(self.count - self.offset, self.limit)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=False,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit