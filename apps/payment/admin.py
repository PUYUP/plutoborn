from django.contrib import admin

from utils.generals import get_model

Payment = get_model('payment', 'TopUp')
Coin = get_model('payment', 'Coin')


class CoinExtend(admin.ModelAdmin):
    model = Coin
    list_display = ('user', 'get_transaction_type_display', 'amount', 'description',)

    def get_readonly_fields(self, request, obj=None):
        # Disallow edit
        if obj:
            exclude_fields = ['amount']
            local_fields = list()

            for field in self.opts.local_fields:
                if field.name not in exclude_fields:
                    local_fields.append(field.name)

            for field in self.opts.local_many_to_many:
                if field.name not in exclude_fields:
                    local_fields.append(field.name)
            return list(set(local_fields))
        return super().get_readonly_fields(request, obj)


admin.site.register(Payment)
admin.site.register(Coin, CoinExtend)
