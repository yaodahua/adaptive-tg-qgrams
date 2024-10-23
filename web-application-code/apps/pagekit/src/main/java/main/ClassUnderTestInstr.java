package main;

import org.openqa.selenium.By;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.openqa.selenium.WebDriver;
import po_utils.DriverProvider;
import custom_classes.*;
import po_utils.NotInTheRightPageObjectException;
import po_utils.NotTheRightInputValuesException;

public class ClassUnderTestInstr {
    private Object currentPage = null;
    private final static Logger logger = Logger.getLogger(ClassUnderTestInstr.class.getName());
    public ClassUnderTestInstr() {
        WebDriver driver = new DriverProvider().getActiveDriver();

        po.signin.SignIn signIn = new po.signin.SignIn(driver);

        signIn.singIn(Username.ADMIN, UserPassword.ADMIN);
        this.currentPage = new po.dashboard.pages.DashboardContainerPage(driver);
    }
    public void cancelOperationSelectLinkPage() {
        if (this.currentPage instanceof po.shared.pages.modals.SelectLinkPage) {
            po.shared.pages.modals.SelectLinkPage page = (po.shared.pages.modals.SelectLinkPage) this.currentPage;

            if (page.poCallee.equals(page.userSettings)) {
                logger.log(Level.INFO, "IF-28");
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@class=\"uk-button uk-button-link uk-modal-close\"]")));
                this.currentPage = new po.users.pages.UserSettingsContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.addEditLink)) {
                logger.log(Level.INFO, "IF-33");
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@class=\"uk-button uk-button-link uk-modal-close\"]")));
                this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.addEditLogin)) {
                logger.log(Level.INFO, "IF-38");
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@class=\"uk-button uk-button-link uk-modal-close\"]")));
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(("Unknown poCallee " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("cancelOperationSelectLinkPage: expected po.shared.pages.modals.SelectLinkPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectLinkPageSelectLinkPage(custom_classes.Extension extension, custom_classes.SitePages sitePage) {
        if (this.currentPage instanceof po.shared.pages.modals.SelectLinkPage) {
            po.shared.pages.modals.SelectLinkPage page = (po.shared.pages.modals.SelectLinkPage) this.currentPage;

            if (extension.value().equals("Page") && page.isOptionPagePresent() && page.isOptionPresentInDropdown(By.id("form-link-page"), sitePage.value())) {
                page.selectOptionInDropdown(org.openqa.selenium.By.id("form-link-page"), sitePage.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@type=\"submit\"]")));
                if (page.poCallee.equals(page.userSettings)) {
                    logger.log(Level.INFO, "IF-69");
                    this.currentPage = new po.users.pages.UserSettingsContainerPage(page.getDriver());
                } else if (page.poCallee.equals(page.addEditLink)) {
                    boolean textExpected = false;

                    java.lang.String text = "false";

                    if (page.waitForElementThatChangesText(org.openqa.selenium.By.xpath("//div[@class=\"uk-form-controls\"]/p[@class=\"uk-text-muted uk-margin-small-top uk-margin-bottom-remove\"]"), textExpected, text)) {
                        logger.log(Level.INFO, "IF-78");
                        this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.getDriver());
                    } else {
                        throw new NotTheRightInputValuesException("update: text not handled properly");
                    }
                } else if (page.poCallee.equals(page.addEditLogin)) {
                    boolean textExpected = false;

                    java.lang.String text = "false";

                    if (page.waitForElementThatChangesText(page.locatorElementToWaitFor, textExpected, text)) {
                        logger.log(Level.INFO, "IF-89");
                        this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.getDriver());
                    } else {
                        throw new NotTheRightInputValuesException("update: text not handled properly");
                    }
                } else {
                    throw new NotTheRightInputValuesException(("selectLinkPage: unknown poCallee " + page.poCallee));
                }
            } else {
                throw new NotTheRightInputValuesException((((("selectLinkPage: extension " + extension.value()) + " is not Page or SitePage ") + sitePage.value()) + " is not among the options or there are no options"));
            }
        } else {
            throw new NotInTheRightPageObjectException("selectLinkPageSelectLinkPage: expected po.shared.pages.modals.SelectLinkPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectLinkStorageSelectLinkPage(custom_classes.Extension extension) {
        if (this.currentPage instanceof po.shared.pages.modals.SelectLinkPage) {
            po.shared.pages.modals.SelectLinkPage page = (po.shared.pages.modals.SelectLinkPage) this.currentPage;

            if (extension.value().equals("Storage")) {
                logger.log(Level.INFO, "IF-118");
                page.selectOptionInDropdown(org.openqa.selenium.By.id("form-style"), extension.value());
                page.clickOn(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal-dialog\"]//a[@class=\"pk-form-link-toggle pk-link-icon uk-flex-middle\"]"));
                java.lang.String currentPoCallee = "SelectLinkPage";

                this.currentPage = new po.shared.pages.modals.SelectImagePage(page.getDriver(), currentPoCallee, page.poCallee);
            } else {
                throw new NotTheRightInputValuesException((("selectLinkStorage: extension " + extension.value()) + " is not Storage"));
            }
        } else {
            throw new NotInTheRightPageObjectException("selectLinkStorageSelectLinkPage: expected po.shared.pages.modals.SelectLinkPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectLinkUserSelectLinkPage(custom_classes.Extension extension, custom_classes.View view) {
        if (this.currentPage instanceof po.shared.pages.modals.SelectLinkPage) {
            po.shared.pages.modals.SelectLinkPage page = (po.shared.pages.modals.SelectLinkPage) this.currentPage;

            if (extension.value().equals("User")) {
                page.selectOptionInDropdown(org.openqa.selenium.By.id("form-style"), extension.value());
                page.selectOptionInDropdown(org.openqa.selenium.By.id("form-link-user"), view.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@type=\"submit\"]")));
                if (page.poCallee.equals(page.userSettings)) {
                    logger.log(Level.INFO, "IF-152");
                    this.currentPage = new po.users.pages.UserSettingsContainerPage(page.getDriver());
                } else if (page.poCallee.equals(page.addEditLink)) {
                    boolean textExpected = false;

                    java.lang.String text = "false";

                    if (page.waitForElementThatChangesText(org.openqa.selenium.By.xpath("//div[@class=\"uk-form-controls\"]/p[@class=\"uk-text-muted uk-margin-small-top uk-margin-bottom-remove\"]"), textExpected, text)) {
                        logger.log(Level.INFO, "IF-161");
                        this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.getDriver());
                    } else {
                        throw new NotTheRightInputValuesException("update: text not handled properly");
                    }
                } else if (page.poCallee.equals(page.addEditLogin)) {
                    boolean textExpected = false;

                    java.lang.String text = "false";

                    if (page.waitForElementThatChangesText(page.locatorElementToWaitFor, textExpected, text)) {
                        logger.log(Level.INFO, "IF-172");
                        this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.getDriver());
                    } else {
                        throw new NotTheRightInputValuesException("update: text not handled properly");
                    }
                } else {
                    throw new NotTheRightInputValuesException(("selectLinkUser: unknown poCallee " + page.poCallee));
                }
            } else {
                throw new NotTheRightInputValuesException((("selectLinkUser: extension " + extension.value()) + " is not User"));
            }
        } else {
            throw new NotInTheRightPageObjectException("selectLinkUserSelectLinkPage: expected po.shared.pages.modals.SelectLinkPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void updateSelectLinkPage() {
        if (this.currentPage instanceof po.shared.pages.modals.SelectLinkPage) {
            po.shared.pages.modals.SelectLinkPage page = (po.shared.pages.modals.SelectLinkPage) this.currentPage;

            if (page.poCallee.equals(page.userSettings)) {
                logger.log(Level.INFO, "IF-199");
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@type=\"submit\"]")));
                this.currentPage = new po.users.pages.UserSettingsContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.addEditLink)) {
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@type=\"submit\"]")));
                boolean textExpected = false;

                java.lang.String text = "false";

                if (page.waitForElementThatChangesText(org.openqa.selenium.By.xpath("//div[@class=\"uk-form-controls\"]/p[@class=\"uk-text-muted uk-margin-small-top uk-margin-bottom-remove\"]"), textExpected, text)) {
                    logger.log(Level.INFO, "IF-212");
                    this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("update: text not handled properly");
                }
            } else if (page.poCallee.equals(page.addEditLogin)) {
                page.clickOn(org.openqa.selenium.By.xpath((page.prefix + "/button[@type=\"submit\"]")));
                boolean textExpected = false;

                java.lang.String text = "false";

                if (page.waitForElementThatChangesText(page.locatorElementToWaitFor, textExpected, text)) {
                    logger.log(Level.INFO, "IF-225");
                    this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("update: text not handled properly");
                }
            } else {
                throw new NotTheRightInputValuesException(("update: unknown poCallee " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("updateSelectLinkPage: expected po.shared.pages.modals.SelectLinkPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void cancelOperationDeleteItemPage() {
        if (this.currentPage instanceof po.shared.pages.modals.DeleteItemPage) {
            po.shared.pages.modals.DeleteItemPage page = (po.shared.pages.modals.DeleteItemPage) this.currentPage;

            if (page.poCallee.equals(page.dashboard)) {
                logger.log(Level.INFO, "IF-248");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.userList)) {
                logger.log(Level.INFO, "IF-253");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.users.pages.UserListContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.roles)) {
                logger.log(Level.INFO, "IF-258");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.users.pages.RolesContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.pages)) {
                logger.log(Level.INFO, "IF-263");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.site.pages.PagesContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(("Unknown PO callee name: " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("cancelOperationDeleteItemPage: expected po.shared.pages.modals.DeleteItemPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void confirmOperationDeleteItemPage() {
        if (this.currentPage instanceof po.shared.pages.modals.DeleteItemPage) {
            po.shared.pages.modals.DeleteItemPage page = (po.shared.pages.modals.DeleteItemPage) this.currentPage;

            if (page.poCallee.equals(page.dashboard)) {
                logger.log(Level.INFO, "IF-284");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link js-modal-confirm\"]"));
                page.waitForTimeoutExpires(500);
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.userList) && page.expectingFailure.equals("default")) {
                logger.log(Level.INFO, "IF-291");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link js-modal-confirm\"]"));
                page.waitForTimeoutExpires(500);
                this.currentPage = new po.users.pages.UserListContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.userList) && page.expectingFailure.equals("Delete admin user")) {
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link js-modal-confirm\"]"));
                if (page.waitForElementBeingPresentOnPage(org.openqa.selenium.By.xpath("//div[@class=\"uk-notify uk-notify-top-center\"]/div[@class=\"uk-notify-message uk-notify-message-danger\"]"))) {
                    logger.log(Level.INFO, "IF-302");
                    this.currentPage = new po.users.pages.UserListContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("ConfirmOperation: unable to delete yourself message not loaded properly");
                }
            } else if (page.poCallee.equals(page.roles)) {
                logger.log(Level.INFO, "IF-309");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link js-modal-confirm\"]"));
                page.waitForTimeoutExpires(500);
                this.currentPage = new po.users.pages.RolesContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.pages)) {
                logger.log(Level.INFO, "IF-315");
                page.clickOn(org.openqa.selenium.By.xpath("//button[@class=\"uk-button uk-button-link js-modal-confirm\"]"));
                page.waitForTimeoutExpires(500);
                this.currentPage = new po.site.pages.PagesContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(("Unknown PO callee name: " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("confirmOperationDeleteItemPage: expected po.shared.pages.modals.DeleteItemPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addItemAddEditItemPage() {
        if (this.currentPage instanceof po.shared.pages.modals.AddEditItemPage) {
            po.shared.pages.modals.AddEditItemPage page = (po.shared.pages.modals.AddEditItemPage) this.currentPage;

            if (page.poCallee.equals(page.roles) && page.expectingFailure.equals("Role already exists")) {
                page.type(org.openqa.selenium.By.xpath((page.xpathPrefix + "//input")), page.formValueInput.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link\"]")));
                if (page.waitForElementBeingPresentOnPage(org.openqa.selenium.By.xpath("//div[@class=\"uk-notify uk-notify-top-center\"]/div[@class=\"uk-notify-message uk-notify-message-danger\"]"))) {
                    logger.log(Level.INFO, "IF-345");
                    this.currentPage = new po.users.pages.RolesContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("addItem: unable to add role message not loaded properly");
                }
            } else if (page.poCallee.equals(page.roles) && page.expectingFailure.equals("default")) {
                page.type(org.openqa.selenium.By.xpath((page.xpathPrefix + "//input")), page.formValueInput.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link\"]")));
                if (page.waitForElementBeingPresentOnPage(org.openqa.selenium.By.xpath("//div[@class=\"uk-notify uk-notify-top-center\"]/div[@class=\"uk-notify-message\"]")) && page.waitForElementBeingInvisibleOnPage(org.openqa.selenium.By.xpath("//div[@class=\"uk-notify uk-notify-top-center\"]/div[@class=\"uk-notify-message\"]"))) {
                    logger.log(Level.INFO, "IF-363");
                    this.currentPage = new po.users.pages.RolesContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("addItem: roles notification not handled properly");
                }
            } else if (page.poCallee.equals(page.pages) && page.expectingFailure.equals("Menu already exists")) {
                page.type(org.openqa.selenium.By.xpath((page.xpathPrefix + "//input")), page.formValueInput.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link\"]")));
                if (page.waitForElementBeingPresentOnPage(org.openqa.selenium.By.xpath("//div[@class=\"uk-notify uk-notify-top-center\"]/div[@class=\"uk-notify-message uk-notify-message-danger\"]"))) {
                    logger.log(Level.INFO, "IF-378");
                    this.currentPage = new po.site.pages.PagesContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("addItem: page notification not handled properly");
                }
            } else if (page.poCallee.equals(page.pages) && page.expectingFailure.equals("default")) {
                page.type(org.openqa.selenium.By.xpath((page.xpathPrefix + "//input")), page.formValueInput.value());
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link\"]")));
                if (page.waitForElementBeingPresentOnPage(org.openqa.selenium.By.xpath((("//ul[@class=\"uk-nav uk-nav-side\"]/li/a[text()=\"" + page.formValueInput.value()) + "\"]")))) {
                    logger.log(Level.INFO, "IF-394");
                    this.currentPage = new po.site.pages.PagesContainerPage(page.getDriver());
                } else {
                    throw new NotTheRightInputValuesException("addItem: page notification not handled properly");
                }
            } else {
                throw new NotTheRightInputValuesException(("Unknown PO callee name: " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("addItemAddEditItemPage: expected po.shared.pages.modals.AddEditItemPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void cancelOperationAddEditItemPage() {
        if (this.currentPage instanceof po.shared.pages.modals.AddEditItemPage) {
            po.shared.pages.modals.AddEditItemPage page = (po.shared.pages.modals.AddEditItemPage) this.currentPage;

            if (page.poCallee.equals(page.roles)) {
                logger.log(Level.INFO, "IF-417");
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link uk-modal-close\"]")));
                this.currentPage = new po.users.pages.RolesContainerPage(page.getDriver());
            } else if (page.poCallee.equals(page.pages)) {
                logger.log(Level.INFO, "IF-422");
                page.clickOn(org.openqa.selenium.By.xpath((page.xpathPrefix + "//button[@class=\"uk-button uk-button-link uk-modal-close\"]")));
                this.currentPage = new po.site.pages.PagesContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(("Unknown PO callee name: " + page.poCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("cancelOperationAddEditItemPage: expected po.shared.pages.modals.AddEditItemPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void cancelOperationSelectImagePage() {
        if (this.currentPage instanceof po.shared.pages.modals.SelectImagePage) {
            po.shared.pages.modals.SelectImagePage page = (po.shared.pages.modals.SelectImagePage) this.currentPage;

            if (page.poCallee.equals(page.linkPage) && !page.previousPoCallee.equals("default")) {
                logger.log(Level.INFO, "IF-443");
                page.clickOn(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal-dialog uk-modal-dialog-large\"]//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.getDriver(), page.previousPoCallee);
            } else if (page.poCallee.equals(page.addEditPage)) {
                logger.log(Level.INFO, "IF-448");
                page.clickOn(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal-dialog uk-modal-dialog-large\"]//button[@class=\"uk-button uk-button-link uk-modal-close\"]"));
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(((("selectFile: unknown poCallee " + page.poCallee) + " or previousCallee is default ") + page.previousPoCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("cancelOperationSelectImagePage: expected po.shared.pages.modals.SelectImagePage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectFileSelectImagePage(custom_classes.FileNames fileName) {
        if (this.currentPage instanceof po.shared.pages.modals.SelectImagePage) {
            po.shared.pages.modals.SelectImagePage page = (po.shared.pages.modals.SelectImagePage) this.currentPage;

            if (page.poCallee.equals(page.linkPage) && !page.previousPoCallee.equals("default")) {
                logger.log(Level.INFO, "IF-469");
                java.util.List<org.openqa.selenium.WebElement> filesInTable = page.findElements(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal uk-open\"]//div[@class=\"uk-form\"]//table/tbody/tr"));

                org.openqa.selenium.WebElement inputCheckbox = page.getIndexMatchingName(filesInTable, fileName);

                page.clickOn(inputCheckbox);
                page.clickOn(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal uk-open\"]//button[@class=\"uk-button uk-button-primary\" and @type=\"button\"]"));
                this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.getDriver(), page.previousPoCallee);
            } else if (page.poCallee.equals(page.addEditPage)) {
                logger.log(Level.INFO, "IF-480");
                java.util.List<org.openqa.selenium.WebElement> filesInTable = page.findElements(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal uk-open\"]//div[@class=\"uk-form\"]//table/tbody/tr"));

                org.openqa.selenium.WebElement inputCheckbox = page.getIndexMatchingName(filesInTable, fileName);

                page.clickOn(inputCheckbox);
                page.clickOn(org.openqa.selenium.By.xpath("//div[@class=\"uk-modal uk-open\"]//button[@class=\"uk-button uk-button-primary\" and @type=\"button\"]"));
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.getDriver());
            } else {
                throw new NotTheRightInputValuesException(((("selectFile: unknown poCallee " + page.poCallee) + " or previousCallee is default ") + page.previousPoCallee));
            }
        } else {
            throw new NotInTheRightPageObjectException("selectFileSelectImagePage: expected po.shared.pages.modals.SelectImagePage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addFeedWidgetDashboardContainerPage(custom_classes.WidgetFeedTitle widgetFeedTitle, custom_classes.WidgetFeedUrl widgetFeedUrl, custom_classes.WidgetFeedNumberOfPosts widgetFeedNumberOfPosts, custom_classes.WidgetFeedPostContent widgetFeedPostContent) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-508");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(Widgets.FEED);
            page.widgetComponent.addEditFeedWidget(widgetFeedTitle, widgetFeedUrl, widgetFeedNumberOfPosts, widgetFeedPostContent);
            this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addFeedWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addLocationWidgetDashboardContainerPage(custom_classes.WidgetLocation widgetLocation, custom_classes.WidgetUnit widgetUnit) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-527");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(Widgets.LOCATION);
            page.widgetComponent.addEditLocationWidget(widgetLocation, widgetUnit);
            this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addLocationWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addUserWidgetDashboardContainerPage(custom_classes.WidgetUserType widgetUserType, custom_classes.WidgetUserDisplay widgetUserDisplay, custom_classes.WidgetTotalUser widgetTotalUser, custom_classes.WidgetNumberOfUsers widgetNumberOfUsers) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-547");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(Widgets.USER);
            page.widgetComponent.addEditUserWidget(widgetUserType, widgetUserDisplay, widgetTotalUser, widgetNumberOfUsers);
            this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addUserWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteLocationWidgetDashboardContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && page.widgetComponent.isLocationWidget(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-568");
                page.widgetComponent.clickOnEditWidget(widgetsOnPage.get((id.value - 1)));
                page.widgetComponent.deleteWidget(widgetsOnPage.get((id.value - 1)));
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a widget"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteLocationWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteUserOrFeedWidgetDashboardContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && !page.widgetComponent.isLocationWidget(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-594");
                page.widgetComponent.clickOnEditWidget(widgetsOnPage.get((id.value - 1)));
                page.widgetComponent.deleteWidget(widgetsOnPage.get((id.value - 1)));
                java.lang.String poCallee = "DashboardContainerPage";

                this.currentPage = new po.shared.pages.modals.DeleteItemPage(page.widgetComponent.getDriver(), poCallee);
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a widget"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteUserOrFeedWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editFeedWidgetDashboardContainerPage(custom_classes.Id id, custom_classes.WidgetFeedTitle widgetFeedTitle, custom_classes.WidgetFeedUrl widgetFeedUrl, custom_classes.WidgetFeedNumberOfPosts widgetFeedNumberOfPosts, custom_classes.WidgetFeedPostContent widgetFeedPostContent) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && page.widgetComponent.isFeedWidget(widgetsOnPage.get(id.value - 1)) && !page.widgetComponent.isWidgetFormOpen(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-623");
                page.widgetComponent.clickOnEditWidget(widgetsOnPage.get((id.value - 1)));
                page.widgetComponent.addEditFeedWidget(widgetFeedTitle, widgetFeedUrl, widgetFeedNumberOfPosts, widgetFeedPostContent);
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a feed widget or the widget form is open"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editFeedWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editLocationWidgetDashboardContainerPage(custom_classes.Id id, custom_classes.WidgetLocation widgetLocation, custom_classes.WidgetUnit widgetUnit) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && page.widgetComponent.isLocationWidget(widgetsOnPage.get(id.value - 1)) && !page.widgetComponent.isWidgetFormOpen(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-650");
                page.widgetComponent.clickOnEditWidget(widgetsOnPage.get((id.value - 1)));
                page.widgetComponent.addEditLocationWidget(widgetLocation, widgetUnit);
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a location widget or the widget form is open"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editLocationWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editUserWidgetDashboardContainerPage(custom_classes.Id id, custom_classes.WidgetUserType widgetUserType, custom_classes.WidgetUserDisplay widgetUserDisplay, custom_classes.WidgetTotalUser widgetTotalUser, custom_classes.WidgetNumberOfUsers widgetNumberOfUsers) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && page.widgetComponent.isUserWidget(widgetsOnPage.get(id.value - 1)) && !page.widgetComponent.isWidgetFormOpen(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-678");
                page.widgetComponent.clickOnEditWidget(widgetsOnPage.get((id.value - 1)));
                page.widgetComponent.addEditUserWidget(widgetUserType, widgetUserDisplay, widgetTotalUser, widgetNumberOfUsers);
                this.currentPage = new po.dashboard.pages.DashboardContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a user widget or the widget form is open"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editUserWidgetDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardDashboardContainerPage() {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-699");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserDashboardContainerPage() {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-711");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditUserDashboardContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> widgetsOnPage = page.widgetsListComponent.getWidgetsOnPage();

            if (id.value - 1 < widgetsOnPage.size() && page.widgetComponent.isUserWidget(widgetsOnPage.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-729");
                page.widgetComponent.clickOnEditUserLink(widgetsOnPage.get((id.value - 1)));
                this.currentPage = new po.users.pages.AddEditUserContainerPage(page.widgetComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("WebElement with id " + id.value) + " is not a user widget"));
            }
        } else {
            throw new NotInTheRightPageObjectException("goToEditUserDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteDashboardContainerPage() {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-747");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersDashboardContainerPage() {
        if (this.currentPage instanceof po.dashboard.pages.DashboardContainerPage) {
            logger.log(Level.INFO, "IF-759");
            po.dashboard.pages.DashboardContainerPage page = (po.dashboard.pages.DashboardContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersDashboardContainerPage: expected po.dashboard.pages.DashboardContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void activateUserUserListContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> users = page.userListComponent.getUsersInList();

            if (id.value - 1 < users.size() && !page.userListComponent.isUserSelected(users.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-775");
                page.userListComponent.activateUser(users.get((id.value - 1)));
                this.currentPage = new po.users.pages.UserListContainerPage(page.userListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("User with id " + id.value) + " is not a valid user"));
            }
        } else {
            throw new NotInTheRightPageObjectException("activateUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addUserUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-792");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            page.userListComponent.clickOn(org.openqa.selenium.By.xpath("//a[@class=\"uk-button uk-button-primary\"]"));
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.userListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void blockUserUserListContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> users = page.userListComponent.getUsersInList();

            if (id.value - 1 < users.size() && !page.userListComponent.isUserSelected(users.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-811");
                page.userListComponent.blockUser(users.get((id.value - 1)));
                this.currentPage = new po.users.pages.UserListContainerPage(page.userListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("User with id " + id.value) + " is not a valid user"));
            }
        } else {
            throw new NotInTheRightPageObjectException("blockUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteAdminUserUserListContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> users = page.userListComponent.getUsersInList();

            if (id.value - 1 < users.size() && !page.userListComponent.isUserSelected(users.get(id.value - 1)) && page.userListComponent.isAdminUser(users.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-832");
                page.userListComponent.deleteUser(users.get((id.value - 1)));
                java.lang.String poCallee = "UserListContainerPage";

                java.lang.String expectingFailure = "Delete admin user";

                this.currentPage = new po.shared.pages.modals.DeleteItemPage(page.userListComponent.getDriver(), poCallee, expectingFailure);
            } else {
                throw new NotTheRightInputValuesException((("User with id " + id.value) + " is not a valid user"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteAdminUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteUserUserListContainerPage(custom_classes.Id id) {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            java.util.List<org.openqa.selenium.WebElement> users = page.userListComponent.getUsersInList();

            if (id.value - 1 < users.size() && !page.userListComponent.isUserSelected(users.get(id.value - 1))) {
                logger.log(Level.INFO, "IF-856");
                page.userListComponent.deleteUser(users.get((id.value - 1)));
                java.lang.String poCallee = "UserListContainerPage";

                this.currentPage = new po.shared.pages.modals.DeleteItemPage(page.userListComponent.getDriver(), poCallee);
            } else {
                throw new NotTheRightInputValuesException((("User with id " + id.value) + " is not a valid user"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-874");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-886");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPermissionsUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-900");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToPermissionsUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToRolesUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-913");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToRolesUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-926");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.USER_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-939");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUserListUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-951");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.LIST);
        } else {
            throw new NotInTheRightPageObjectException("goToUserListUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersUserListContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserListContainerPage) {
            logger.log(Level.INFO, "IF-963");
            po.users.pages.UserListContainerPage page = (po.users.pages.UserListContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersUserListContainerPage: expected po.users.pages.UserListContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addExistingUserRoleRolesContainerPage(custom_classes.UserRoles userRole) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (page.rolesSidebarComponent.isRolePresent(userRole)) {
                logger.log(Level.INFO, "IF-978");
                java.lang.String poCallee = "RolesContainerPage";

                java.lang.String expectingFailure = "Role already exists";

                page.rolesSidebarComponent.addRole();
                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.rolesSidebarComponent.getDriver(), poCallee, userRole, expectingFailure);
            } else {
                throw new NotTheRightInputValuesException((("addExistingUserRole: user role " + userRole.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addExistingUserRoleRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addUserRoleRolesContainerPage(custom_classes.UserRoles userRole) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (!page.rolesSidebarComponent.isRolePresent(userRole)) {
                logger.log(Level.INFO, "IF-1000");
                page.rolesSidebarComponent.addRole();
                java.lang.String poCallee = "RolesContainerPage";

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.rolesSidebarComponent.getDriver(), poCallee, userRole);
            } else {
                throw new NotTheRightInputValuesException((("addUserRole: user role " + userRole.value()) + " already exists"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addUserRoleRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteUserRoleRolesContainerPage(custom_classes.UserRoles userRoleToDelete) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (page.rolesSidebarComponent.isRolePresent(userRoleToDelete) && page.rolesSidebarComponent.isRoleEditable(userRoleToDelete)) {
                logger.log(Level.INFO, "IF-1022");
                page.rolesSidebarComponent.deleteRole(userRoleToDelete);
                java.lang.String poCallee = "RolesContainerPage";

                this.currentPage = new po.shared.pages.modals.DeleteItemPage(page.rolesSidebarComponent.getDriver(), poCallee);
            } else {
                throw new NotTheRightInputValuesException((("deleteUserRole: user role " + userRoleToDelete.value()) + " is not present or not editable"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteUserRoleRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editUserRoleRolesContainerPage(custom_classes.UserRoles userRoleToEdit, custom_classes.UserRoles newUserRole) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (page.rolesSidebarComponent.isRolePresent(userRoleToEdit) && page.rolesSidebarComponent.isRoleEditable(userRoleToEdit)) {
                logger.log(Level.INFO, "IF-1045");
                page.rolesSidebarComponent.editRole(userRoleToEdit);
                java.lang.String poCallee = "RolesContainerPage";

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.rolesMainComponent.getDriver(), poCallee, newUserRole);
            } else {
                throw new NotTheRightInputValuesException((("editUserRole: user role " + userRoleToEdit.value()) + " is not editable or it does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editUserRoleRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editUserRoleWithExistingOneRolesContainerPage(custom_classes.UserRoles userRoleToEdit, custom_classes.UserRoles existingUserRole) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (page.rolesSidebarComponent.isRolePresent(userRoleToEdit) && page.rolesSidebarComponent.isRoleEditable(userRoleToEdit) && page.rolesSidebarComponent.isRolePresent(existingUserRole)) {
                logger.log(Level.INFO, "IF-1068");
                page.rolesSidebarComponent.editRole(userRoleToEdit);
                java.lang.String poCallee = "RolesContainerPage";

                java.lang.String expectingFailure = "Role already exists";

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.rolesMainComponent.getDriver(), poCallee, existingUserRole, expectingFailure);
            } else {
                throw new NotTheRightInputValuesException((((("editUserRole: user role " + userRoleToEdit.value()) + " is not editable or it does not exist or new user role ") + existingUserRole.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editUserRoleWithExistingOneRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void giveOrRemoveAllPermissionsToUserRoleRolesContainerPage(custom_classes.UserRoles userRoles) {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            if (page.rolesSidebarComponent.isRolePresent(userRoles) && !page.rolesSidebarComponent.isRoleAdmin(userRoles)) {
                logger.log(Level.INFO, "IF-1093");
                page.rolesSidebarComponent.clickOnRole(userRoles);
                page.rolesMainComponent.giveOrRemoveAllPermissionsToUserRole();
                this.currentPage = new po.users.pages.RolesContainerPage(page.rolesSidebarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("giveOrRemoveAllPermissionsToUserRole: user role " + userRoles.value()) + " is not present or it is an admin role"));
            }
        } else {
            throw new NotInTheRightPageObjectException("giveOrRemoveAllPermissionsToUserRoleRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1112");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1124");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPermissionsRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1138");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToPermissionsRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToRolesRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1151");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToRolesRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1164");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.USER_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1177");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUserListRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1189");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.LIST);
        } else {
            throw new NotInTheRightPageObjectException("goToUserListRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersRolesContainerPage() {
        if (this.currentPage instanceof po.users.pages.RolesContainerPage) {
            logger.log(Level.INFO, "IF-1201");
            po.users.pages.RolesContainerPage page = (po.users.pages.RolesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersRolesContainerPage: expected po.users.pages.RolesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addUserAddEditUserContainerPage(custom_classes.Username username, custom_classes.Name name, custom_classes.Email email, custom_classes.UserPassword userPassword, custom_classes.UserStatus userStatus) {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            if (!page.addEditUserComponent.isEditUser()) {
                logger.log(Level.INFO, "IF-1219");
                page.addEditUserComponent.addUser(username, name, email, userPassword, userStatus);
                this.currentPage = new po.users.pages.AddEditUserContainerPage(page.addEditUserComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addUser: you are in edit user mode");
            }
        } else {
            throw new NotInTheRightPageObjectException("addUserAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeOperationAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1237");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            page.addEditUserComponent.closeOperation();
            this.currentPage = new po.users.pages.UserListContainerPage(page.addEditUserComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("closeOperationAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editUserAddEditUserContainerPage(custom_classes.Username username, custom_classes.Name name, custom_classes.Email email, custom_classes.UserPassword userPassword) {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            if (page.addEditUserComponent.isEditUser()) {
                logger.log(Level.INFO, "IF-1255");
                page.addEditUserComponent.editUser(username, name, email, userPassword);
                this.currentPage = new po.users.pages.AddEditUserContainerPage(page.addEditUserComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("editUser: you are not in edit user mode");
            }
        } else {
            throw new NotInTheRightPageObjectException("editUserAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1273");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1285");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPermissionsAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1299");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToPermissionsAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToRolesAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1312");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToRolesAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1325");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.USER_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1338");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUserListAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1350");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.LIST);
        } else {
            throw new NotInTheRightPageObjectException("goToUserListAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditUserContainerPage() {
        if (this.currentPage instanceof po.users.pages.AddEditUserContainerPage) {
            logger.log(Level.INFO, "IF-1362");
            po.users.pages.AddEditUserContainerPage page = (po.users.pages.AddEditUserContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditUserContainerPage: expected po.users.pages.AddEditUserContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void giveOrRemoveAllPermissionsToUserRolePermissionsContainerPage(custom_classes.UserRoles userRoles) {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            if (page.permissionsComponent.getUserRoles().contains(userRoles.value()) && !page.permissionsComponent.isRoleAdministrator(userRoles)) {
                logger.log(Level.INFO, "IF-1378");
                page.permissionsComponent.giveOrRemoveAllPermissionsToUserRole(userRoles);
                this.currentPage = new po.users.pages.PermissionsContainerPage(page.permissionsComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("giveOrRemoveAllPermissionsToUserRole: user role " + userRoles.value()) + " does not exist or it is an administrator role."));
            }
        } else {
            throw new NotInTheRightPageObjectException("giveOrRemoveAllPermissionsToUserRolePermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1397");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1409");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPermissionsPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1423");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToPermissionsPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToRolesPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1436");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToRolesPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1449");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.USER_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSitePermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1462");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSitePermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUserListPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1474");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.LIST);
        } else {
            throw new NotInTheRightPageObjectException("goToUserListPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersPermissionsContainerPage() {
        if (this.currentPage instanceof po.users.pages.PermissionsContainerPage) {
            logger.log(Level.INFO, "IF-1486");
            po.users.pages.PermissionsContainerPage page = (po.users.pages.PermissionsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersPermissionsContainerPage: expected po.users.pages.PermissionsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void changeSettingsUserSettingsContainerPage(custom_classes.RegistrationUserSettings registrationUserSettings) {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1499");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            page.userSettingsComponent.changeSettings(registrationUserSettings);
            java.lang.String poCallee = "UserSettingsContainerPage";

            this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.userSettingsComponent.getDriver(), poCallee);
        } else {
            throw new NotInTheRightPageObjectException("changeSettingsUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1514");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1526");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPermissionsUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1540");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToPermissionsUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToRolesUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1553");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PERMISSIONS);
        } else {
            throw new NotInTheRightPageObjectException("goToRolesUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1566");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.USER_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1579");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUserListUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1591");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.LIST);
        } else {
            throw new NotInTheRightPageObjectException("goToUserListUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1603");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void saveSettingsUserSettingsContainerPage() {
        if (this.currentPage instanceof po.users.pages.UserSettingsContainerPage) {
            logger.log(Level.INFO, "IF-1615");
            po.users.pages.UserSettingsContainerPage page = (po.users.pages.UserSettingsContainerPage) this.currentPage;

            page.userSettingsComponent.clickOn(org.openqa.selenium.By.xpath("//div[@id=\"settings\"]//button[@class=\"uk-button uk-button-primary\"]"));
            this.currentPage = new po.users.pages.UserSettingsContainerPage(page.userSettingsComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("saveSettingsUserSettingsContainerPage: expected po.users.pages.UserSettingsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addExistingMenuPagesContainerPage(custom_classes.SiteMenus siteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesSidebarComponent.isMenuPresent(siteMenu) && !page.pagesSidebarComponent.isSpecialMenu(siteMenu)) {
                logger.log(Level.INFO, "IF-1635");
                page.pagesSidebarComponent.addMenu();
                java.lang.String poCallee = page.getClass().getSimpleName();

                java.lang.String expectingFailure = "Menu already exists";

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.pagesSidebarComponent.getDriver(), poCallee, siteMenu, expectingFailure);
            } else {
                throw new NotTheRightInputValuesException((("addExistingMenu: menu " + siteMenu.value()) + " is not present or it is a special menu."));
            }
        } else {
            throw new NotInTheRightPageObjectException("addExistingMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addLinkPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (!page.pagesSidebarComponent.isTrashMenuActive()) {
                logger.log(Level.INFO, "IF-1657");
                page.pagesListComponent.addLinkOrPage(SiteAddPage.LINK);
                this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addLink: trash menu active, not possible to add page");
            }
        } else {
            throw new NotInTheRightPageObjectException("addLinkPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addMenuPagesContainerPage(custom_classes.SiteMenus siteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (!page.pagesSidebarComponent.isMenuPresent(siteMenu) && !page.pagesSidebarComponent.isSpecialMenu(siteMenu)) {
                logger.log(Level.INFO, "IF-1676");
                page.pagesSidebarComponent.addMenu();
                java.lang.String poCallee = page.getClass().getSimpleName();

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.pagesSidebarComponent.getDriver(), poCallee, siteMenu);
            } else {
                throw new NotTheRightInputValuesException((("addMenu: menu " + siteMenu.value()) + " is present or it is a special menu."));
            }
        } else {
            throw new NotInTheRightPageObjectException("addMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addPagePagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (!page.pagesSidebarComponent.isTrashMenuActive()) {
                logger.log(Level.INFO, "IF-1697");
                page.pagesListComponent.addLinkOrPage(SiteAddPage.PAGE);
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addPage: trash menu active, not possible to add page");
            }
        } else {
            throw new NotInTheRightPageObjectException("addPagePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteAllPagesAndLinksPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-1716");
                page.pagesListComponent.selectAll();
                page.pagesListComponent.delete();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("deleteAllPagesAndLinks: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteAllPagesAndLinksPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteLinkOrPagePagesContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(siteLinkOrPage)) {
                logger.log(Level.INFO, "IF-1737");
                page.pagesListComponent.selectLinkOrPage(siteLinkOrPage);
                page.pagesListComponent.delete();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("deleteLinkOrPage: siteLinkOrPage " + siteLinkOrPage.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteLinkOrPagePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editLinkPagesContainerPage(custom_classes.SiteLinks siteLink) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(siteLink)) {
                logger.log(Level.INFO, "IF-1758");
                page.pagesListComponent.editLinkOrPage(siteLink);
                this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("editLink: siteLink " + siteLink.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editLinkPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editMenuPagesContainerPage(custom_classes.SiteMenus siteMenu, custom_classes.SiteMenus newNameSiteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesSidebarComponent.isMenuPresent(siteMenu) && page.pagesSidebarComponent.isMenuEditable(siteMenu) && !page.pagesSidebarComponent.isSpecialMenu(newNameSiteMenu) && !page.pagesSidebarComponent.isMenuPresent(newNameSiteMenu)) {
                logger.log(Level.INFO, "IF-1778");
                page.pagesSidebarComponent.editMenu(siteMenu);
                java.lang.String poCallee = page.getClass().getSimpleName();

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.pagesSidebarComponent.getDriver(), poCallee, newNameSiteMenu);
            } else {
                throw new NotTheRightInputValuesException((((("editMenu: menu " + siteMenu.value()) + " not present or not editable. Or new menu ") + newNameSiteMenu.value()) + " is a special menu or it already exists"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editMenuWithExistingMenuPagesContainerPage(custom_classes.SiteMenus siteMenu, custom_classes.SiteMenus newNameSiteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesSidebarComponent.isMenuPresent(siteMenu) && page.pagesSidebarComponent.isMenuEditable(siteMenu) && page.pagesSidebarComponent.isMenuPresent(newNameSiteMenu) && !page.pagesSidebarComponent.isSpecialMenu(newNameSiteMenu) && !siteMenu.value().equals(newNameSiteMenu.value())) {
                logger.log(Level.INFO, "IF-1806");
                page.pagesSidebarComponent.editMenu(siteMenu);
                java.lang.String poCallee = page.getClass().getSimpleName();

                java.lang.String expectingFailure = "Menu already exists";

                this.currentPage = new po.shared.pages.modals.AddEditItemPage(page.pagesSidebarComponent.getDriver(), poCallee, newNameSiteMenu, expectingFailure);
            } else {
                throw new NotTheRightInputValuesException((((("editMenuWithExistingMenu: menu " + siteMenu.value()) + " not present or not editable. Or new menu ") + newNameSiteMenu.value()) + " does not exist or it is a special menu. Or the two menus are the same"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editMenuWithExistingMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editPagePagesContainerPage(custom_classes.SitePages sitePage) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(sitePage)) {
                logger.log(Level.INFO, "IF-1830");
                page.pagesListComponent.editLinkOrPage(sitePage);
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("editPage: sitePage " + sitePage.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editPagePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1847");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1859");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToMenuPagesContainerPage(custom_classes.SiteMenus siteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesSidebarComponent.isMenuPresent(siteMenu)) {
                logger.log(Level.INFO, "IF-1875");
                page.pagesSidebarComponent.clickOnLink(siteMenu);
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesSidebarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("goToMenu: siteMenu " + siteMenu.value()) + " not present"));
            }
        } else {
            throw new NotInTheRightPageObjectException("goToMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1892");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSitePagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1904");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSitePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1916");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            logger.log(Level.INFO, "IF-1928");
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void moveAllPagesAndLinksToMenuPagesContainerPage(custom_classes.SiteMenus siteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesSidebarComponent.isMenuPresent(siteMenu) && page.pagesListComponent.isOneElementPresent() && !page.pagesSidebarComponent.isTrashMenu(siteMenu)) {
                logger.log(Level.INFO, "IF-1944");
                page.pagesListComponent.selectAll();
                page.pagesListComponent.move(siteMenu);
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesSidebarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("moveAllPagesAndLinksToMenu: siteMenu " + siteMenu.value()) + " does not exist or there are no links nor pages"));
            }
        } else {
            throw new NotInTheRightPageObjectException("moveAllPagesAndLinksToMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void moveLinkOrPageToMenuPagesContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage, custom_classes.SiteMenus siteMenu) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(siteLinkOrPage) && page.pagesSidebarComponent.isMenuPresent(siteMenu) && !page.pagesSidebarComponent.isTrashMenu(siteMenu)) {
                logger.log(Level.INFO, "IF-1968");
                page.pagesListComponent.selectLinkOrPage(siteLinkOrPage);
                page.pagesListComponent.move(siteMenu);
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((((("moveLinkOrPageToMenu: siteLinkOrPage " + siteLinkOrPage.value()) + " does not exist or siteMenu ") + siteMenu.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("moveLinkOrPageToMenuPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void publishAllPagesAndLinksPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-1990");
                page.pagesListComponent.selectAll();
                page.pagesListComponent.publish();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("publishAllPagesAndLinks: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("publishAllPagesAndLinksPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void publishLinkOrPagePagesContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(siteLinkOrPage) && !page.pagesListComponent.isStatusActive(siteLinkOrPage)) {
                logger.log(Level.INFO, "IF-2011");
                page.pagesListComponent.selectLinkOrPage(siteLinkOrPage);
                page.pagesListComponent.publish();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("publishLinkOrPage: siteLinkOrPage " + siteLinkOrPage.value()) + " does not exist or it is active"));
            }
        } else {
            throw new NotInTheRightPageObjectException("publishLinkOrPagePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void unpublishAllPagesAndLinksPagesContainerPage() {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-2032");
                page.pagesListComponent.selectAll();
                page.pagesListComponent.unpublish();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("unpublishAllPagesAndLinks: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("unpublishAllPagesAndLinksPagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void unpublishLinkOrPagePagesContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage) {
        if (this.currentPage instanceof po.site.pages.PagesContainerPage) {
            po.site.pages.PagesContainerPage page = (po.site.pages.PagesContainerPage) this.currentPage;

            if (page.pagesListComponent.isLinkOrPagePresent(siteLinkOrPage) && page.pagesListComponent.isStatusActive(siteLinkOrPage)) {
                logger.log(Level.INFO, "IF-2054");
                page.pagesListComponent.selectLinkOrPage(siteLinkOrPage);
                page.pagesListComponent.unpublish();
                this.currentPage = new po.site.pages.PagesContainerPage(page.pagesListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("unpublishLinkOrPage: siteLinkOrPage " + siteLinkOrPage.value()) + " does not exist or it is not active"));
            }
        } else {
            throw new NotInTheRightPageObjectException("unpublishLinkOrPagePagesContainerPage: expected po.site.pages.PagesContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditMetaAddEditPageContainerPage(custom_classes.SitePages sitePage, custom_classes.MetaDescriptions metaDescription) {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Meta")) {
                logger.log(Level.INFO, "IF-2077");
                page.metaComponent.typeTitle(sitePage.value());
                page.metaComponent.typeDescription(metaDescription.value());
                page.metaComponent.selectImage();
                java.lang.String poCallee = page.getClass().getSimpleName();

                this.currentPage = new po.shared.pages.modals.SelectImagePage(page.menuComponent.getDriver(), poCallee);
            } else {
                throw new NotTheRightInputValuesException("addEditMeta: navbar action active is not meta");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditMetaAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditPageAddEditPageContainerPage(custom_classes.SitePages sitePage, custom_classes.HTMLSnippets htmlSnippet, custom_classes.PageLinkStatus pageLinkStatus, custom_classes.HideInMenu hideInMenu) {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Content")) {
                logger.log(Level.INFO, "IF-2103");
                page.HTMLFormComponent.enterTitle(sitePage.value());
                page.HTMLFormComponent.writeIntoTextarea(htmlSnippet.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.hideOnMenu(hideInMenu.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addEditPage: navbar action active is not page");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditPageAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditPageRestrictAccessAddEditPageContainerPage(custom_classes.SitePages sitePage, custom_classes.HTMLSnippets htmlSnippet, custom_classes.PageLinkStatus pageLinkStatus, custom_classes.UserRoles userRole, custom_classes.HideInMenu hideInMenu) {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Content") && page.pageLinkDetailsComponent.isRolePresent(userRole.value())) {
                logger.log(Level.INFO, "IF-2134");
                page.HTMLFormComponent.enterTitle(sitePage.value());
                page.HTMLFormComponent.writeIntoTextarea(htmlSnippet.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.clickOnRole(userRole.value());
                page.pageLinkDetailsComponent.hideOnMenu(hideInMenu.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditPageContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditPage: navbar action active is not page or user role " + userRole.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditPageRestrictAccessAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeEditPageAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2158");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.close(AddEditNavbarPoCallees.PAGE_LINK);
        } else {
            throw new NotInTheRightPageObjectException("closeEditPageAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToContentAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2171");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.PAGE_CONTENT);
        } else {
            throw new NotInTheRightPageObjectException("goToContentAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2184");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2196");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToMetaAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2210");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.PAGE_META);
        } else {
            throw new NotInTheRightPageObjectException("goToMetaAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2223");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2235");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2247");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsAddEditPageContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditPageContainerPage) {
            logger.log(Level.INFO, "IF-2259");
            po.site.pages.AddEditPageContainerPage page = (po.site.pages.AddEditPageContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsAddEditPageContainerPage: expected po.site.pages.AddEditPageContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditTextWidgetAddEditTextWidgetContainerPage(custom_classes.WidgetTextTitles widgetTextTitle, custom_classes.HTMLSnippets htmlSnippet, custom_classes.PageLinkStatus pageLinkStatus) {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Settings")) {
                logger.log(Level.INFO, "IF-2276");
                page.htmlFormComponent.enterTitle(widgetTextTitle.value());
                page.htmlFormComponent.writeIntoTextarea(htmlSnippet.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addEditTextWidget: navbar item active is not Settings");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditTextWidgetAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditTextWidgetRestrictAccessAddEditTextWidgetContainerPage(custom_classes.WidgetTextTitles widgetTextTitle, custom_classes.HTMLSnippets htmlSnippet, custom_classes.PageLinkStatus pageLinkStatus, custom_classes.UserRoles userRole) {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Settings") && page.pageLinkDetailsComponent.isRolePresent(userRole.value())) {
                logger.log(Level.INFO, "IF-2305");
                page.htmlFormComponent.enterTitle(widgetTextTitle.value());
                page.htmlFormComponent.writeIntoTextarea(htmlSnippet.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.clickOnRole(userRole.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditTextWidget: navbar item active is not Settings or user role " + userRole.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditTextWidgetRestrictAccessAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditVisibilityToLinkOrPageAddEditTextWidgetContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage) {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Visibility") && page.visibilityComponent.isLinkOrPagePresent(siteLinkOrPage.value())) {
                logger.log(Level.INFO, "IF-2333");
                page.visibilityComponent.clickOnPageInput(siteLinkOrPage.value());
                this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditVisibility: navbar item active is not Visibility or link or page " + siteLinkOrPage.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditVisibilityToLinkOrPageAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeEditTextAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2352");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.close(AddEditNavbarPoCallees.MENU_TEXT_LOGIN);
        } else {
            throw new NotInTheRightPageObjectException("closeEditTextAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2365");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2377");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2391");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2403");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.TEXT_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2416");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2428");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToVisibilityAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2440");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.TEXT_VISIBILITY);
        } else {
            throw new NotInTheRightPageObjectException("goToVisibilityAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsAddEditTextWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            logger.log(Level.INFO, "IF-2453");
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void restrictVisibilityAddEditTextWidgetContainerPage(custom_classes.SitePages sitePage) {
        if (this.currentPage instanceof po.site.pages.AddEditTextWidgetContainerPage) {
            po.site.pages.AddEditTextWidgetContainerPage page = (po.site.pages.AddEditTextWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Visibility") && page.visibilityComponent.isLinkOrPagePresent(sitePage.value())) {
                logger.log(Level.INFO, "IF-2470");
                page.visibilityComponent.clickOnPageInput(sitePage.value());
                this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("restrictVisibility: navbar item active is not visibility");
            }
        } else {
            throw new NotInTheRightPageObjectException("restrictVisibilityAddEditTextWidgetContainerPage: expected po.site.pages.AddEditTextWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditMetaAddEditLinkContainerPage(custom_classes.SiteLinks siteLink, custom_classes.MetaDescriptions metaDescription) {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Meta")) {
                logger.log(Level.INFO, "IF-2491");
                page.metaComponent.typeTitle(siteLink.value());
                page.metaComponent.typeDescription(metaDescription.value());
                page.metaComponent.selectImage();
                java.lang.String poCallee = page.getClass().getSimpleName();

                this.currentPage = new po.shared.pages.modals.SelectImagePage(page.menuComponent.getDriver(), poCallee);
            } else {
                throw new NotTheRightInputValuesException("addEditMeta: navbar action active is not meta");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditMetaAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addLinkAddEditLinkContainerPage(custom_classes.PageLinkStatus pageLinkStatus, custom_classes.LinkTypes linkType, custom_classes.SiteLinks siteLink, custom_classes.HideInMenu hideInMenu) {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            if (page.addEditLinkFormComponent.isUrlPresent()) {
                logger.log(Level.INFO, "IF-2517");
                page.addEditLinkFormComponent.selectLinkType(linkType.value());
                page.pageLinkDetailsComponent.typeTitle(siteLink.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.hideOnMenu(hideInMenu.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.addEditLinkFormComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("Url is not present");
            }
        } else {
            throw new NotInTheRightPageObjectException("addLinkAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addLinkRestrictAccessAddEditLinkContainerPage(custom_classes.PageLinkStatus pageLinkStatus, custom_classes.LinkTypes linkType, custom_classes.UserRoles userRole, custom_classes.SiteLinks siteLink, custom_classes.HideInMenu hideInMenu) {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            if (page.addEditLinkFormComponent.isUrlPresent() && page.pageLinkDetailsComponent.isRolePresent(userRole.value())) {
                logger.log(Level.INFO, "IF-2547");
                page.addEditLinkFormComponent.selectLinkType(linkType.value());
                page.pageLinkDetailsComponent.typeTitle(siteLink.value());
                page.pageLinkDetailsComponent.clickOnRole(userRole.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.hideOnMenu(hideInMenu.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditLinkContainerPage(page.addEditLinkFormComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("Url is not present or user role " + userRole.value()) + " is not present"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addLinkRestrictAccessAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeEditLinkAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2571");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.close(AddEditNavbarPoCallees.PAGE_LINK);
        } else {
            throw new NotInTheRightPageObjectException("closeEditLinkAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2584");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2596");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToMetaAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2610");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.LINK_META);
        } else {
            throw new NotInTheRightPageObjectException("goToMetaAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2623");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2635");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.LINK_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2648");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2660");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2672");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectUrlAddEditLinkContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLinkContainerPage) {
            logger.log(Level.INFO, "IF-2684");
            po.site.pages.AddEditLinkContainerPage page = (po.site.pages.AddEditLinkContainerPage) this.currentPage;

            page.addEditLinkFormComponent.selectUrl();
            java.lang.String poCallee = page.getClass().getSimpleName();

            this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.addEditLinkFormComponent.getDriver(), poCallee);
        } else {
            throw new NotInTheRightPageObjectException("selectUrlAddEditLinkContainerPage: expected po.site.pages.AddEditLinkContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addLoginWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2699");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(SiteAddWidget.LOGIN);
            this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addLoginWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addMenuWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2713");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(SiteAddWidget.MENU);
            this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addMenuWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addTextWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2727");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            page.widgetsListComponent.addWidget(SiteAddWidget.TEXT);
            this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.widgetsListComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("addTextWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void copyAllWidgetsWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-2743");
                page.widgetsListComponent.selectAll();
                page.widgetsListComponent.copy();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("copy: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("copyAllWidgetsWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void copyWidgetWidgetsContainerPage(custom_classes.Widget widget) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widget)) {
                logger.log(Level.INFO, "IF-2763");
                page.widgetsListComponent.selectWidget(widget);
                page.widgetsListComponent.copy();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("copy: widget " + widget.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("copyWidgetWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteAllWidgetsWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-2783");
                page.widgetsListComponent.selectAll();
                page.widgetsListComponent.delete();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("deleteAllWidgets: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteAllWidgetsWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void deleteWidgetWidgetsContainerPage(custom_classes.Widget widget) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widget)) {
                logger.log(Level.INFO, "IF-2803");
                page.widgetsListComponent.selectWidget(widget);
                page.widgetsListComponent.delete();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("deleteWidget: widget " + widget.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("deleteWidgetWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editLoginWidgetsContainerPage(custom_classes.WidgetLoginTitles widgetLoginTitle) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widgetLoginTitle)) {
                logger.log(Level.INFO, "IF-2824");
                page.widgetsListComponent.editWidget(widgetLoginTitle);
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("editLogin: widgetLoginTitle " + widgetLoginTitle.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editLoginWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editMenuWidgetsContainerPage(custom_classes.WidgetMenuTitles widgetMenuTitle) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widgetMenuTitle)) {
                logger.log(Level.INFO, "IF-2845");
                page.widgetsListComponent.editWidget(widgetMenuTitle);
                this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("editMenu: widgetMenuTitle " + widgetMenuTitle.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editMenuWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void editTextWidgetsContainerPage(custom_classes.WidgetTextTitles widgetTextTitle) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widgetTextTitle)) {
                logger.log(Level.INFO, "IF-2866");
                page.widgetsListComponent.editWidget(widgetTextTitle);
                this.currentPage = new po.site.pages.AddEditTextWidgetContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("editText: widgetTextTitle " + widgetTextTitle.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("editTextWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2884");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2896");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToMenuWidgetsContainerPage(custom_classes.WidgetMenus widgetMenu) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsSidebarComponent.isMenuPresent(widgetMenu)) {
                logger.log(Level.INFO, "IF-2913");
                page.widgetsSidebarComponent.clickOnLink(widgetMenu);
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsSidebarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("goToMenu: widgetMenu " + widgetMenu.value()) + " not present"));
            }
        } else {
            throw new NotInTheRightPageObjectException("goToMenuWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2930");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2942");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2954");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            logger.log(Level.INFO, "IF-2966");
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void publishAllWidgetsWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-2980");
                page.widgetsListComponent.selectAll();
                page.widgetsListComponent.publish();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("publishAllWidgets: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("publishAllWidgetsWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void publishWidgetWidgetsContainerPage(custom_classes.Widget widget) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widget) && !page.widgetsListComponent.isStatusActive(widget)) {
                logger.log(Level.INFO, "IF-3001");
                page.widgetsListComponent.selectWidget(widget);
                page.widgetsListComponent.publish();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("publishWidget: widget " + widget.value()) + " does not exist or it is active"));
            }
        } else {
            throw new NotInTheRightPageObjectException("publishWidgetWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void unpublishAllWidgetsWidgetsContainerPage() {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isOneElementPresent()) {
                logger.log(Level.INFO, "IF-3021");
                page.widgetsListComponent.selectAll();
                page.widgetsListComponent.unpublish();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("unpublishAllWidgets: there must be at least one element in the list");
            }
        } else {
            throw new NotInTheRightPageObjectException("unpublishAllWidgetsWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void unpublishWidgetWidgetsContainerPage(custom_classes.Widget widget) {
        if (this.currentPage instanceof po.site.pages.WidgetsContainerPage) {
            po.site.pages.WidgetsContainerPage page = (po.site.pages.WidgetsContainerPage) this.currentPage;

            if (page.widgetsListComponent.isWidgetPresent(widget) && page.widgetsListComponent.isStatusActive(widget)) {
                logger.log(Level.INFO, "IF-3042");
                page.widgetsListComponent.selectWidget(widget);
                page.widgetsListComponent.unpublish();
                this.currentPage = new po.site.pages.WidgetsContainerPage(page.widgetsListComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("unpublishWidget: widget " + widget.value()) + " does not exist or it is not active"));
            }
        } else {
            throw new NotInTheRightPageObjectException("unpublishWidgetWidgetsContainerPage: expected po.site.pages.WidgetsContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditLoginDetailsAddEditLoginWidgetContainerPage(custom_classes.WidgetLoginTitles widgetLoginTitle, custom_classes.PageLinkStatus pageLinkStatus) {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (!page.addEditNavbarComponent.isNavbarItemActive("Visibility")) {
                logger.log(Level.INFO, "IF-3064");
                page.addEditLoginWidgetComponent.typeTitle(widgetLoginTitle.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addEditLoginDetails: visibility tab is active, cannot add login details");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditLoginDetailsAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditLoginDetailsRestrictAccessAddEditLoginWidgetContainerPage(custom_classes.WidgetLoginTitles widgetLoginTitle, custom_classes.PageLinkStatus pageLinkStatus, custom_classes.UserRoles userRole) {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (page.pageLinkDetailsComponent.isRolePresent(userRole.value()) && !page.addEditNavbarComponent.isNavbarItemActive("Visibility")) {
                logger.log(Level.INFO, "IF-3092");
                page.addEditLoginWidgetComponent.typeTitle(widgetLoginTitle.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.pageLinkDetailsComponent.clickOnRole(userRole.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.pageLinkDetailsComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditLoginDetailsRestrictAccess: user role " + userRole.value()) + " does not exist or visibility tab is active"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditLoginDetailsRestrictAccessAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditLoginDetailsWithUrlAddEditLoginWidgetContainerPage(custom_classes.WidgetLoginTitles widgetLoginTitle, custom_classes.PageLinkStatus pageLinkStatus) {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (page.addEditLoginWidgetComponent.isUrlLoginPresent() && page.addEditLoginWidgetComponent.isUrlLogoutPresent() && !page.addEditNavbarComponent.isNavbarItemActive("Visibility")) {
                logger.log(Level.INFO, "IF-3120");
                page.addEditLoginWidgetComponent.typeTitle(widgetLoginTitle.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.addEditLoginWidgetComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("addEditLoginDetailsWithUrl: url login or url logout is not present or visibility tab is active");
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditLoginDetailsWithUrlAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeEditLoginAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3141");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.close(AddEditNavbarPoCallees.MENU_TEXT_LOGIN);
        } else {
            throw new NotInTheRightPageObjectException("closeEditLoginAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3154");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3166");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3180");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3192");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.LOGIN_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3205");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3217");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToVisibilityAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3229");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.LOGIN_VISIBILITY);
        } else {
            throw new NotInTheRightPageObjectException("goToVisibilityAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3242");
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void restrictVisibilityAddEditLoginWidgetContainerPage(custom_classes.SitePages sitePage) {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Visibility") && page.visibilityComponent.isLinkOrPagePresent(sitePage.value())) {
                logger.log(Level.INFO, "IF-3259");
                page.visibilityComponent.clickOnPageInput(sitePage.value());
                this.currentPage = new po.site.pages.AddEditLoginWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("restrictVisibility: navbar item active is not visibility");
            }
        } else {
            throw new NotInTheRightPageObjectException("restrictVisibilityAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectLoginRedirectLinkAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (!page.addEditNavbarComponent.isNavbarItemActive("Visibility")) {
                logger.log(Level.INFO, "IF-3278");
                page.addEditLoginWidgetComponent.selectLoginRedirect();
                java.lang.String poCallee = page.getClass().getSimpleName();

                org.openqa.selenium.By locatorToWaitFor = org.openqa.selenium.By.xpath("(//div[@class=\"uk-form-controls\"]/p[@class=\"uk-text-muted uk-margin-small-top uk-margin-bottom-remove\"])[1]");

                this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.addEditLoginWidgetComponent.getDriver(), poCallee, locatorToWaitFor);
            } else {
                throw new NotTheRightInputValuesException("selectLoginRedirectLink: visibility tab is active, cannot select login redirect link");
            }
        } else {
            throw new NotInTheRightPageObjectException("selectLoginRedirectLinkAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void selectLogoutRedirectLinkAddEditLoginWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditLoginWidgetContainerPage) {
            po.site.pages.AddEditLoginWidgetContainerPage page = (po.site.pages.AddEditLoginWidgetContainerPage) this.currentPage;

            if (!page.addEditNavbarComponent.isNavbarItemActive("Visibility")) {
                logger.log(Level.INFO, "IF-3301");
                page.addEditLoginWidgetComponent.selectLogoutRedirect();
                java.lang.String poCallee = page.getClass().getSimpleName();

                org.openqa.selenium.By locatorToWaitFor = org.openqa.selenium.By.xpath("(//div[@class=\"uk-form-controls\"]/p[@class=\"uk-text-muted uk-margin-small-top uk-margin-bottom-remove\"])[2]");

                this.currentPage = new po.shared.pages.modals.SelectLinkPage(page.addEditLoginWidgetComponent.getDriver(), poCallee, locatorToWaitFor);
            } else {
                throw new NotTheRightInputValuesException("selectLogoutRedirectLink: visibility tab is active, cannot select logout redirect link");
            }
        } else {
            throw new NotInTheRightPageObjectException("selectLogoutRedirectLinkAddEditLoginWidgetContainerPage: expected po.site.pages.AddEditLoginWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditMenuDetailsAddEditMenuWidgetContainerPage(custom_classes.WidgetMenuTitles widgetMenuTitle, custom_classes.SiteMenus siteMenu, custom_classes.StartLevel startLevel, custom_classes.Depth depth, custom_classes.MenuSubItems menuSubItem, custom_classes.PageLinkStatus pageLinkStatus) {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            if (page.addEditMenuWidgetComponent.isMenuPresent(siteMenu.value())) {
                logger.log(Level.INFO, "IF-3329");
                page.addEditMenuWidgetComponent.typeTitle(widgetMenuTitle.value());
                page.addEditMenuWidgetComponent.selectMenu(siteMenu.value());
                page.addEditMenuWidgetComponent.selectLevel(startLevel.value);
                page.addEditMenuWidgetComponent.selectDepth(depth.value());
                page.addEditMenuWidgetComponent.selectSubItems(menuSubItem.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.addEditMenuWidgetComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditMenuDetails: siteMenu " + siteMenu.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditMenuDetailsAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditMenuDetailsRestrictAccessAddEditMenuWidgetContainerPage(custom_classes.WidgetMenuTitles widgetMenuTitle, custom_classes.SiteMenus siteMenu, custom_classes.StartLevel startLevel, custom_classes.Depth depth, custom_classes.MenuSubItems menuSubItem, custom_classes.PageLinkStatus pageLinkStatus, custom_classes.UserRoles userRole) {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            if (page.addEditMenuWidgetComponent.isMenuPresent(siteMenu.value()) && page.pageLinkDetailsComponent.isRolePresent(userRole.value())) {
                logger.log(Level.INFO, "IF-3363");
                page.addEditMenuWidgetComponent.typeTitle(widgetMenuTitle.value());
                page.addEditMenuWidgetComponent.selectMenu(siteMenu.value());
                page.addEditMenuWidgetComponent.selectLevel(startLevel.value);
                page.addEditMenuWidgetComponent.selectDepth(depth.value());
                page.addEditMenuWidgetComponent.selectSubItems(menuSubItem.value());
                page.pageLinkDetailsComponent.clickOnRole(userRole.value());
                page.pageLinkDetailsComponent.selectStatus(pageLinkStatus.value());
                page.addEditNavbarComponent.save();
                this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.addEditMenuWidgetComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((((("addEditMenuDetails: siteMenu " + siteMenu.value()) + " does not exist or user role ") + userRole.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditMenuDetailsRestrictAccessAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void addEditVisibilityToLinkOrPageAddEditMenuWidgetContainerPage(custom_classes.SiteLinkOrPage siteLinkOrPage) {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Visibility") && page.visibilityComponent.isLinkOrPagePresent(siteLinkOrPage.value())) {
                logger.log(Level.INFO, "IF-3394");
                page.visibilityComponent.clickOnPageInput(siteLinkOrPage.value());
                this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException((("addEditVisibility: navbar item active is not Visibility or link or page " + siteLinkOrPage.value()) + " does not exist"));
            }
        } else {
            throw new NotInTheRightPageObjectException("addEditVisibilityToLinkOrPageAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void closeEditMenuAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3413");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.close(AddEditNavbarPoCallees.MENU_TEXT_LOGIN);
        } else {
            throw new NotInTheRightPageObjectException("closeEditMenuAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToDashboardAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3426");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.DASHBOARD);
        } else {
            throw new NotInTheRightPageObjectException("goToDashboardAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToEditCurrentUserAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3438");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            page.menuComponent.goToEditCurrentUser();
            this.currentPage = new po.users.pages.AddEditUserContainerPage(page.menuComponent.getDriver());
        } else {
            throw new NotInTheRightPageObjectException("goToEditCurrentUserAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToPagesAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3452");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.PAGES);
        } else {
            throw new NotInTheRightPageObjectException("goToPagesAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSettingsAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3464");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.MENU_SETTINGS);
        } else {
            throw new NotInTheRightPageObjectException("goToSettingsAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToSiteAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3477");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.SITE);
        } else {
            throw new NotInTheRightPageObjectException("goToSiteAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToUsersAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3489");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.menuComponent.goTo(MenuActions.USERS);
        } else {
            throw new NotInTheRightPageObjectException("goToUsersAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToVisibilityAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3501");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.addEditNavbarComponent.goTo(AddEditNavbarActions.MENU_VISIBILITY);
        } else {
            throw new NotInTheRightPageObjectException("goToVisibilityAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void goToWidgetsAddEditMenuWidgetContainerPage() {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            logger.log(Level.INFO, "IF-3514");
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            this.currentPage = page.navbarComponent.goTo(NavbarActions.WIDGETS);
        } else {
            throw new NotInTheRightPageObjectException("goToWidgetsAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
    public void restrictVisibilityAddEditMenuWidgetContainerPage(custom_classes.SitePages sitePage) {
        if (this.currentPage instanceof po.site.pages.AddEditMenuWidgetContainerPage) {
            po.site.pages.AddEditMenuWidgetContainerPage page = (po.site.pages.AddEditMenuWidgetContainerPage) this.currentPage;

            if (page.addEditNavbarComponent.isNavbarItemActive("Visibility") && page.visibilityComponent.isLinkOrPagePresent(sitePage.value())) {
                logger.log(Level.INFO, "IF-3531");
                page.visibilityComponent.clickOnPageInput(sitePage.value());
                this.currentPage = new po.site.pages.AddEditMenuWidgetContainerPage(page.addEditNavbarComponent.getDriver());
            } else {
                throw new NotTheRightInputValuesException("restrictVisibility: navbar item active is not visibility");
            }
        } else {
            throw new NotInTheRightPageObjectException("restrictVisibilityAddEditMenuWidgetContainerPage: expected po.site.pages.AddEditMenuWidgetContainerPage, found " + this.currentPage.getClass().getSimpleName());
        }
    }
}