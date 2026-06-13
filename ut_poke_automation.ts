export async function automation(ctx: { payload: { message?: string, type?: string } }) {
    const { message, type } = ctx.payload;
    
    if (!message) return null;

    return `[UT Portal Monitor] ${type === 'alert' ? '🚨 ALERT: ' : ''}${message}`;
}
