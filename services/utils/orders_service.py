class OrdersService:

    @classmethod
    async def get_orders_count(cls, orders: list):
        delivered = 0
        canceled = 0
        another = 0
        print(f"\n\nZAKAZI \n{orders}\n\n")
        for order in orders:
            status = order['status']
            if status == 'CANCELLED':
                canceled += 1
            elif status == 'DELIVERED':
                delivered += 1
            else:
                another += 1

        return delivered, canceled, another

    @classmethod
    async def get_orders_by_status(cls, orders: list, status: str):
        orders_sorted = []
        for order in orders:
            if status == 'ANOTHER':
                if order['status'] != 'DELIVERED' and order['status'] != 'CANCELLED':
                    orders_sorted.append(order)
                else:
                    ...
            else:
                if order['status'] == status:
                    orders_sorted.append(order)
                else:
                    ...
        return orders_sorted




