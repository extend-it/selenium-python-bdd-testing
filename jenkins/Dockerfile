# Local Jenkins controller with Python, Chromium + chromedriver and the Allure CLI baked in.
# Debian's Chromium is used instead of Google Chrome so the image also builds on ARM64.
FROM jenkins/jenkins:lts-jdk17

USER root

# Allure 2 command-line tool used by the Allure Jenkins plugin to render reports.
# Check https://github.com/allure-framework/allure2/releases for the current version.
# Keep in sync with ALLURE_VERSION in the GitHub Actions ui-tests.yml workflow.
ARG ALLURE_VERSION=2.32.0

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-pip \
        chromium chromium-driver \
        fonts-liberation rsync curl \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL -o /tmp/allure.tgz \
        "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" \
 && tar -xzf /tmp/allure.tgz -C /opt \
 && mv "/opt/allure-${ALLURE_VERSION}" /opt/allure \
 && ln -s /opt/allure/bin/allure /usr/local/bin/allure \
 && rm /tmp/allure.tgz

# Tell the test framework (conftest.py) to use the distro browser and driver.
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    HEADLESS=1

USER jenkins

# Skip the setup wizard; configuration comes from JCasC.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc/jenkins.yaml

COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY --chown=jenkins:jenkins casc/ /usr/share/jenkins/ref/casc/
COPY --chown=jenkins:jenkins init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/
