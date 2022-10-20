import pickle
import os


def get_saved_jobs(jobs_dir="../jobs/linked_in/") -> list:
    rv = []
    for item in os.listdir(jobs_dir):
        job = pickle.load(open(os.path.join(jobs_dir, item), 'rb'))
        rv.append(job)
    return rv


def main():
    jobs = get_saved_jobs()
    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()
