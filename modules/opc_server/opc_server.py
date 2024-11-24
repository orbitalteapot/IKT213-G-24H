# opc_server.py

import time
from opcua import Server, ua


class OpcuaServer:
    def __init__(self, endpoint, uri, callback=None):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.server.set_server_name("CablelayServer")
        self.callback = callback
        idx = self.server.register_namespace(uri)

        top_obj = self.server.nodes.objects.add_object(idx, "Cablelay")
        self.filter_obj = top_obj.add_object(idx, "Filters")
        self.zone_obj = top_obj.add_object(idx, "Zones")
        self.height_obj = top_obj.add_object(idx, "Height Data")

        self.variables = {
            'height1': self.height_obj.add_variable(idx, "height1", ua.Variant(0.0, ua.VariantType.Float)),
            'height2': self.height_obj.add_variable(idx, "height2", ua.Variant(0.0, ua.VariantType.Float)),
            'height3': self.height_obj.add_variable(idx, "height3", ua.Variant(0.0, ua.VariantType.Float)),
            'noisefilter': self.filter_obj.add_variable(idx, "noisefilter", ua.Variant(0, ua.VariantType.Int32)),
            'gamma': self.filter_obj.add_variable(idx, "gamma", ua.Variant(0, ua.VariantType.Int32)),
            'contrast': self.filter_obj.add_variable(idx, "contrast", ua.Variant(0, ua.VariantType.Int32)),
            'zone1': self.zone_obj.add_variable(idx, "zone1", ua.Variant(0, ua.VariantType.Int32)),
            'zone2': self.zone_obj.add_variable(idx, "zone2", ua.Variant(0, ua.VariantType.Int32)),
            'zone3': self.zone_obj.add_variable(idx, "zone3", ua.Variant(0, ua.VariantType.Int32))}
        for var in self.variables.values():
            var.set_writable()

        self.server.start()

        self.subscriptions = {}
        self.create_subscriptions()

    def create_subscriptions(self):
        # Pass reverse mapping of nodes to variable names
        handler = SubscriptionHandler(self.callback, {var: name for name, var in self.variables.items()})
        subscription = self.server.create_subscription(1000, handler)
        for var_name, variable in self.variables.items():
            handle = subscription.subscribe_data_change(variable)
            self.subscriptions[var_name] = handle

    def update_variable(self, var_name, value):
        if var_name in self.variables:
            try:
                variant_value = ua.Variant(value, ua.VariantType.Float)  # or ua.VariantType.Double
                self.variables[var_name].set_value(variant_value)
            except Exception as e:
                print(f"Error updating variable {var_name}: {e}")
        else:
            print(f"Variable {var_name} not found")

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.server.stop()
        print("Server stopped")


class SubscriptionHandler:
    def __init__(self, callback, node_to_var_map):
        self.callback = callback
        self.node_to_var_map = node_to_var_map

    def datachange_notification(self, node, val, data):
        # Get the variable name from the node
        var_name = self.node_to_var_map.get(node, None)
        if self.callback and var_name:
            self.callback(var_name, val)

    def event_notification(self, event):
        print("Event Notification", event)
