class Signal:
    def __init__(self, name, props):
        self.name = name
        self.props = props
        self.data_type = props.get("datatype", "")
        self.allowed = props.get("allowed", [])
        self.current_value = None
        self.temp_value = None

    def __repr__(self):
        return f"Signal({self.name}, type={self.data_type}, current={self.current_value}, temp={self.temp_value})"
