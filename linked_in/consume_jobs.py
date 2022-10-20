import pickle
import os


def get_saved_jobs(jobs_dir="../jobs/linked_in/") -> list:
    rv = []
    for item in os.listdir(jobs_dir):
        job = pickle.load(open(os.path.join(jobs_dir, item), 'rb'))
        rv.append(job)
    return rv


def filter_jobs(jobs: list, case_insensitive: bool = True) -> list:
    words_in_description_include = (
        'equivalent experience',
        'python',

    )
    words_in_description_exclude = (
        'intern',
        'student',
        'graduate',
        'pHd'
    )
    rv = []
    for job in jobs:
        for word_exclude in words_in_description_exclude:
            pass
    return rv


def filter_jobs2(jobs: list, case_insensitive: bool = True) -> list:
    words_description_exclude = (
        'intern',
        'student',
        'graduate',
        'pHd',
        'msc'
    )
    words_description_include = (
        'equivalent experience',
    )

    description_exclude = (lambda x: word.upper() if case_insensitive else word not in x for word in
                           words_description_exclude)

    description_include = (lambda x: word.upper() if case_insensitive else word in x for word in
                           words_description_exclude)
    rv = []
    for job in jobs:
        for exclude in description_exclude:
            print(exclude(job.job_description))
    return rv


def main():
    jobs = get_saved_jobs()
    filter_jobs2(jobs)


if __name__ == "__main__":
    main()
