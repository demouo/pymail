from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pymail-notify",  # 因为 pymail 可能已被使用，所以使用 pymail-notify
    version="0.1.3",
    author="xingmo",
    author_email="xingmo_scut@163.com",
    description="一个简单而强大的Python邮件通知工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/demouo/pymail",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
    ],
    package_data={
        "pymail": ["i18n/*.yaml"],
    },
)
