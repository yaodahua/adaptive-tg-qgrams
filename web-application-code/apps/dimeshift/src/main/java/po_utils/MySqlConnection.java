package po_utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

public class MySqlConnection {

    public MySqlConnection(){
    }

    public void insertStatement(Connection connection, String sqlInsertScript){
        try {
            Statement statement = connection.createStatement();
            statement.executeUpdate(sqlInsertScript);
            this.closeStatement(statement);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public Optional<Connection> establishDBConnection(String username, String password, int port, String dbName){
        // This will load the MySQL driver, each DB has its own driver
        try {
            Class.forName("com.mysql.cj.jdbc.Driver").newInstance();
            // Setup the connection with the DB
            Connection connection = DriverManager.getConnection("jdbc:mysql://dimeshift:" + port + "/" + dbName, username, password);
            return Optional.of(connection);
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return Optional.empty();
    }

    public void resetTables(Connection connection, String dbName, List<String> tables){
        try {
            Statement statement = connection.createStatement();
            tables.stream().forEach(new Consumer<String>() {
                @Override
                public void accept(String table) {
                    try {
                        statement.executeUpdate("delete from " + dbName + "." + table);
                    } catch (SQLException e) {
                        e.printStackTrace();
                    }
                }
            });
            this.closeStatement(statement);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private void closeStatement(Statement statement){
        try {
            statement.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void closeConnection(Connection connection){
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
