__version__ = "0.post1"
__git_commiter_name__ = "Itai Shirav"
__git_commiter_email__ = "itais@infinidat.com"
__git_branch__ = u'develop'
__git_remote_tracking_branch__ = '(No remote tracking)'
__git_remote_url__ = '(Not remote tracking)'
__git_head_hash__ = 'ff0aa9321b0819aa2975889762623cb01c9bb466'
__git_head_subject__ = u'added all project files'
__git_head_message__ = u''
__git_dirty_diff__ = u'diff --git a/buildout.cfg b/buildout.cfg\nindex dc52818..8d796c0 100644\n--- a/buildout.cfg\n+++ b/buildout.cfg\n@@ -4,14 +4,14 @@ newest = false\n extensions = buildout.wheel\n download-cache = .cache\n develop = .\n-parts = \n+parts =\n \n [project]\n name = date-detector\n company = Infinidat\n namespace_packages = []\n install_requires = [\'setuptools\']\n-version_file = src/date-detector/__version__.py\n+version_file = src/date_detector/__version__.py\n description = A Python module for scanning text and extracting dates from it\n long_description = A Python module for scanning text and extracting dates from it\n console_scripts = []\ndiff --git a/src/date-detector/__init__.py b/src/date-detector/__init__.py\ndeleted file mode 100644\nindex 5284146..0000000\n--- a/src/date-detector/__init__.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-__import__("pkg_resources").declare_namespace(__name__)\n'
__git_commit_date__ = '2017-12-25 06:13:25'
