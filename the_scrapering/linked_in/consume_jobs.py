import pickle
import os
from the_scrapering.common.jobposting import JobPosting
from copy import deepcopy

def get_saved_jobs(jobs_dir="../jobs/linked_in/"):
    rv = []
    for item in os.listdir(jobs_dir):
        job = pickle.load(open(os.path.join(jobs_dir, item), 'rb'))
        rv.append(job)
    return rv


def requires_phd(jobdescription) -> bool:
    if 'PHD' in jobdescription and 'EQUIVALENT EXPERIENCE' not in jobdescription:
        return True
    return False


def keep_languages(jobs: list, languages_to_keep: iter, verbose=True) -> dict:
    """
    Warning! List mutability

    :param jobs: List mutated
    :param languages_to_keep:
    :return: a dict with the jobs that were removed from jobs
    """
    removed_jobs = dict()
    for n, job in enumerate(jobs):
        assert isinstance(job, JobPosting)
        lang = job.language_posted
        if lang not in removed_jobs.keys() and lang not in languages_to_keep:
            removed_jobs[lang] = list()
        if lang not in languages_to_keep:
            removed_jobs[lang].append(job)

    for lang, _jobs in removed_jobs.items():
        for job in _jobs:
            jobs.remove(job)

    total = 0
    if verbose:
        for lang, _removed_jobs in removed_jobs.items():
            total += len(_removed_jobs)
            print(f"{len(_removed_jobs)} '{lang}' entries.")
    print(f"Total removed due to languages: {total}")

    return removed_jobs


def main():
    removed_jobs = list()
    jobs_description_contain = {
        'AUTOMATION': [],
        'PYTHON': [],
    }
    max_applicatns = 5
    jobs = get_saved_jobs()
    jobs.sort()

    # Keep only wanted languages on 'jobs' list.
    # WARNING: list mutability
    wanted_languages = 'en,nl,es'.split(",")
    lang_removed_jobs = keep_languages(jobs, wanted_languages)

    for job in jobs:
        assert isinstance(job, JobPosting)
        for word, matches in jobs_description_contain.items():
            if word in job.description.upper() and job.applicants <= max_applicatns and not requires_phd(
                    job.description.upper()):
                matches.append(job)

    jobs_description_contain_pre = deepcopy(jobs_description_contain)

    print(1)
    # for k,v in jobs_contain.items():
    #     for _ in v:
    #         print(_.posted_date)


if __name__ == "__main__":
    main()
