using MySqlConnector;
using Npgsql;
using Rkis.Core;

namespace Rkis.Adapters;

public sealed class PostgresProducts(NpgsqlDataSource dataSource) : IProductRepository
{
    public async Task<IReadOnlyList<Product>> ReadAsync(CancellationToken ct)
    {
        await using var command = dataSource.CreateCommand("SELECT id, name, price, version FROM products ORDER BY id");
        await using var reader = await command.ExecuteReaderAsync(ct);
        var rows = new List<Product>();
        while (await reader.ReadAsync(ct))
            rows.Add(new Product(reader.GetInt32(0), reader.GetString(1), reader.GetDecimal(2), reader.GetInt32(3)));
        return rows;
    }
    public async Task<bool> RenameAsync(int id, int expectedVersion, string name, CancellationToken ct)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);
        await using var command = dataSource.CreateCommand("UPDATE products SET name = $1, version = version + 1 WHERE id = $2 AND version = $3");
        command.Parameters.Add(new NpgsqlParameter<string> { TypedValue = name });
        command.Parameters.Add(new NpgsqlParameter<int> { TypedValue = id });
        command.Parameters.Add(new NpgsqlParameter<int> { TypedValue = expectedVersion });
        return await command.ExecuteNonQueryAsync(ct) == 1;
    }
}

public sealed class MySqlProducts(string connectionString) : IProductRepository
{
    public async Task<IReadOnlyList<Product>> ReadAsync(CancellationToken ct)
    {
        await using var connection = new MySqlConnection(connectionString);
        await connection.OpenAsync(ct);
        await using var command = new MySqlCommand("SELECT id, name, price, version FROM products ORDER BY id", connection);
        await using var reader = await command.ExecuteReaderAsync(ct);
        var rows = new List<Product>();
        while (await reader.ReadAsync(ct))
            rows.Add(new Product(reader.GetInt32(0), reader.GetString(1), reader.GetDecimal(2), reader.GetInt32(3)));
        return rows;
    }
    public async Task<bool> RenameAsync(int id, int expectedVersion, string name, CancellationToken ct)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);
        await using var connection = new MySqlConnection(connectionString);
        await connection.OpenAsync(ct);
        await using var command = new MySqlCommand("UPDATE products SET name = @name, version = version + 1 WHERE id = @id AND version = @version", connection);
        command.Parameters.AddWithValue("@name", name);
        command.Parameters.AddWithValue("@id", id);
        command.Parameters.AddWithValue("@version", expectedVersion);
        return await command.ExecuteNonQueryAsync(ct) == 1;
    }
}
