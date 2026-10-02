// Registers the Allure CLI baked into the image (/opt/allure) as the Jenkins tool "allure",
// which the pipelines reference with  allure commandline: 'allure', ...
// If this fails (e.g. the plugin renamed its classes again), configure it by hand:
//   Manage Jenkins > Tools > Allure Commandline > Add > Name: allure, uncheck "Install automatically",
//   Installation directory: /opt/allure
import jenkins.model.Jenkins

import java.lang.reflect.Array
import java.util.logging.Logger

def log = Logger.getLogger('allure-tool.groovy')

// Plugin 3.x moved its classes from ru.yandex.qatools.allure.jenkins to org.allurereport.jenkins.
def candidateClasses = [
    'org.allurereport.jenkins.tools.AllureCommandlineInstallation',
    'ru.yandex.qatools.allure.jenkins.tools.AllureCommandlineInstallation',
]

try {
    def jenkins = Jenkins.get()
    def loader = jenkins.pluginManager.uberClassLoader
    def cls = candidateClasses.findResult { name ->
        try {
            Class.forName(name, true, loader)
        } catch (ClassNotFoundException ignored) {
            null
        }
    }
    if (cls == null) {
        throw new ClassNotFoundException("none of ${candidateClasses}")
    }
    def installation = cls.newInstance('allure', '/opt/allure', [])
    def installations = Array.newInstance(cls, 1)
    installations[0] = installation
    def descriptor = jenkins.getDescriptor(cls)
    descriptor.setInstallations(installations)
    descriptor.save()
    log.info("Allure Commandline tool \"allure\" registered at /opt/allure (${cls.name})")
} catch (Throwable t) {
    log.warning("Could not register the Allure tool automatically: ${t}")
}
