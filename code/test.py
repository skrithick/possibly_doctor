from possibly import doctor

def main():
    question = 'How do I treat diarrhoea?'
    
    print(f'Asking: \'{question}\'\n')
    result = doctor.query(question)
    
    if result:
        
        print(f'Urgency:\t{result.urgency_level}')
        print(f'Confidence:\t{result.confidence}')
        print(f'Overconfidence:\t{result.overconfidence}')
        print(f'Response: \n{result.response}\n')
        print(f'Citations:\t{result.citations}')
    else:
        print('\nNo response')

if __name__ == '__main__':
    main()