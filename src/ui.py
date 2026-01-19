def clear_line(): 
    print("-" * 40)

def title(text): 
    clear_line()
    print(text)
    clear_line

def pause(): 
    input("\nPress the Enter button to continue!")

def menu(prompt, options):
    while True: 
        print("\n" + prompt)
        for i, option in enumerate(options, start = 1):
            print(f"{i}. {option}")
        choice = input("Choose your option: ").strip()

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice 
            
        print("Invalid choice provided. Please try again.")

    