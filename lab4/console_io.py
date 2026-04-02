class ConsoleIO:
    
    @staticmethod
    def input_field(prompt, example="", required=True):
        while True:
            try:
                if example:
                    print(f"Пример: {example}")
                value = input(f"{prompt}: ").strip()
                if required and not value:
                    print("Поле не может быть пустым. Попробуйте снова.")
                    continue
                return value
            except KeyboardInterrupt:
                print("\nВвод прерван.")
                return ""
    
    @staticmethod
    def input_field_int(prompt, min_val=None, max_val=None, required=True):
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if not value:
                    if required:
                        print("Поле не может быть пустым.")
                        continue
                    return 0
                
                num = int(value)
                
                if min_val is not None and num < min_val:
                    print(f"Число должно быть не меньше {min_val}.")
                    continue
                
                if max_val is not None and num > max_val:
                    print(f"Число должно быть не больше {max_val}.")
                    continue
                
                return num
            except ValueError:
                print("Пожалуйста, введите целое число.")
    
    @staticmethod
    def input_field_float(prompt, min_val=None, max_val=None, required=True):
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if not value:
                    if required:
                        print("Поле не может быть пустым.")
                        continue
                    return 0.0
                
                num = float(value)
                
                if min_val is not None and num < min_val:
                    print(f"Число должно быть не меньше {min_val}.")
                    continue
                
                if max_val is not None and num > max_val:
                    print(f"Число должно быть не больше {max_val}.")
                    continue
                
                return num
            except ValueError:
                print("Пожалуйста, введите число.")
    
    @staticmethod
    def input_field_bool(prompt):
        while True:
            try:
                value = input(f"{prompt}: ").strip().lower()
                if value in ['да', 'д', 'yes', 'y', '1', 'true', '+']:
                    return True
                elif value in ['нет', 'н', 'no', 'n', '0', 'false', '-']:
                    return False
                else:
                    print("Пожалуйста, введите 'да' или 'нет'.")
            except KeyboardInterrupt:
                print("\nВвод прерван.")
                return False
    
    @staticmethod
    def output_field(field_name, value):
        print(f"  {field_name}: {value}")
    
    @staticmethod
    def display_message(message):
        print(message)
    
    @staticmethod
    def display_error(error_message):
        print(f"Ошибка: {error_message}")
    
    @staticmethod
    def display_success(message):
        print(message)
    
    @staticmethod
    def display_separator():
        print("=" * 50)
    
    @staticmethod
    def display_header(title):
        print("\n" + "=" * 50)
        print(title)
        print("=" * 50)