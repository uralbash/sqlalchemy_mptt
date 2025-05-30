Releasing
=========

1. Merge all intended and verified pull requests into the ``master`` branch.
2. Create a local build and test:
    - Run ``uv run noxfile.py -s build`` to create a source distribution and a wheel.
    - Install both artifacts in a fresh virtual environment to ensure they work correctly.
3. Bump the version number in ``setup.py``. (May be included in the pull request.)
4. Update the changelog in ``CHANGES.rst``.
5. Add new contributors to the ``CONTRIBUTORS.rst`` file.
6. Update the release date in ``CHANGES.rst``.
7. Ensure the latest build passes on GitHub Actions.
8. Rebuild the documentation and check that it looks correct.
9. Create a new release on GitHub:
   - Use the version number as the tag.
   - Include the changelog in the release notes.
10. Ensure the release is published.
11. Test the release by installing it in a fresh virtual environment.
