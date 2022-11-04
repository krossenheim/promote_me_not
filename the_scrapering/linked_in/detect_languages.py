from django import setup
import pathlib
import sys, os

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(f"{project_root}/promote_me_not")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()
from display_jobs.models import JobPosting


def main():
    jbs = JobPosting.objects.all()
    l = list()
    for jb in jbs:
        l.append(jb.language_posted)
    for item in set(l):
        print(item, l.count(item))


if __name__ == "__main__":
    main()
