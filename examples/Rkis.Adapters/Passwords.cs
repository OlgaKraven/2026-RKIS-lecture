using Microsoft.AspNetCore.Identity;

namespace Rkis.Adapters;
public sealed record User(int Id, string Login);
public static class Passwords
{
    public static string Create(User user, string password)
        => new PasswordHasher<User>().HashPassword(user, password);
    public static PasswordVerificationResult Verify(User user, string stored, string candidate)
        => new PasswordHasher<User>().VerifyHashedPassword(user, stored, candidate);
    public static bool IsLocked(DateTimeOffset now, DateTimeOffset? until)
        => until is not null && now < until.Value;
}
