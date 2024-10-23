package main;

import custom_classes.*;
import po_utils.ResetAppState;
import po_utils.NotInTheRightPageObjectException;
import po_utils.NotTheRightInputValuesException;

public class MainClean {

    public static void main(String[] args) throws InterruptedException {
        
    }

    private static void runWithExceptionHandling(Runnable action) {
        try {
            action.run();
        } catch (NotInTheRightPageObjectException | NotTheRightInputValuesException e) {
            StackTraceElement[] stackTrace = e.getStackTrace();
            if (stackTrace.length > 0) {
                StackTraceElement element = stackTrace[stackTrace.length - 1];
                System.out.println("Exception thrown in method: " + element.getMethodName() + " at line: " + element.getLineNumber());
            }
        }
    }
}
