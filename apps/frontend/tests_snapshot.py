from django.test import TestCase


class UiSnapshotTests(TestCase):
    def test_wizard_snapshot_core_structure(self):
        response = self.client.get("/wizard/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="wizard"', html=False)
        self.assertContains(response, 'id="wizardProgress"', html=False)
        self.assertContains(response, 'id="wizardDynamicContainer"', html=False)
        self.assertContains(response, 'id="validationBanner"', html=False)
        self.assertContains(response, 'id="conflictBanner"', html=False)
        self.assertContains(response, 'id="btnPrev"', html=False)
        self.assertContains(response, 'id="btnNext"', html=False)
        self.assertContains(response, 'id="btnSave"', html=False)
        self.assertContains(response, 'id="btnFieldMode"', html=False)

    def test_dashboard_snapshot_core_structure(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="dashboard"', html=False)
        self.assertContains(response, 'id="dashboardKpis"', html=False)
        self.assertContains(response, 'id="dashboardAlerts"', html=False)
        self.assertContains(response, 'id="dashboardComparatives"', html=False)
        self.assertContains(response, 'id="historyTable"', html=False)
        self.assertContains(response, 'id="aggregateTable"', html=False)
        self.assertContains(response, 'id="roiTable"', html=False)
        self.assertContains(response, 'id="projectsTable"', html=False)
        self.assertContains(response, 'id="reportsTable"', html=False)
