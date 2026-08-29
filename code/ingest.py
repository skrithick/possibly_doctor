from possibly import doctor

def main():
    print('Starting ingestion')

    doctor.csv('data/medquad.csv')
    doctor.md('data', '*.md')
    doctor.embed()

    print('\nIngestion complete.')

if __name__ == '__main__':
    main()