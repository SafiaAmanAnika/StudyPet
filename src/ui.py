def clear_line(): 
    print("-" * 40)

def title(text): 
    clear_line()
    print(text)
    clear_line()

def pause():
    try:
        input("\nPress the Enter button to continue!")
    except KeyboardInterrupt:
        print("\nExiting pause.")

def menu(prompt, options):
    if not options:
        print("No options available.")
        return None

    while True: 
        print("\n" + prompt)
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        choice = input("Choose your option: ").strip()

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice
            
        print("Invalid choice provided. Please try again.")