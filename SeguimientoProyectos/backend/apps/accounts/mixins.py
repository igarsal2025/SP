class CompanySitecQuerysetMixin:
    """Filtra queryset por company/sitec si el modelo lo soporta."""

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        company = getattr(self.request, "company", None)
        sitec = getattr(self.request, "sitec", None)

        model = queryset.model
        if company and hasattr(model, "company_id"):
            queryset = queryset.filter(company=company)
        if sitec and hasattr(model, "sitec_id"):
            queryset = queryset.filter(sitec=sitec)
        return queryset
