// WoofJS host API and selected globals type declarations.

declare namespace __WoofJS__ {
    // Arithmetic helpers used by Math / operators
    function add(a: number, b: number): number;
    function subtract(a: number, b: number): number;
    function mutiply(a: number, b: number): number; // note: spelling kept for compatibility
    function divide(a: number, b: number): number;

    // Core numeric primitives
    const NotANumber: number;
    const Infinity: number;
    const primitiveValues: {
        undefined: undefined;
    };

    // Optional microtask hook used by Promise
    function queueMicrotask(fn: () => void): void;

    // Console backing streams
    class __WoofJS__IO_Stream {
        append(str: string): void;
        setText(str: string): void;
        getText(): string;
        readLine?(): string; // stdin only
        read?(size?: number): string; // stdin only
    }

    const stdin: __WoofJS__IO_Stream;
    const stdout: __WoofJS__IO_Stream;
    const stderr: __WoofJS__IO_Stream;

    // Misc host helpers referenced by stdlib
    function preventExtensions(obj: object): void;
    function getCurrentUnixTimestamp(options?: {
        y2k38safe?: boolean;
        inMilliseconds?: boolean;
    }): number;
    function getRandomFraction(): number;
}

// Minimal Promise typings used by the WoofJS stdlib
declare class Promise<T = any> {
    constructor(
        executor: (
            resolve: (value?: T | PromiseLike<T>) => void,
            reject: (reason?: any) => void
        ) => void
    );

    then<TResult1 = T, TResult2 = never>(
        onfulfilled?: (value: T) => TResult1 | PromiseLike<TResult1>,
        onrejected?: (reason: any) => TResult2 | PromiseLike<TResult2>
    ): Promise<TResult1 | TResult2>;

    catch<TResult = never>(
        onrejected?: (reason: any) => TResult | PromiseLike<TResult>
    ): Promise<T | TResult>;

    finally(onfinally?: () => void): Promise<T>;

    static resolve<T>(value: T | PromiseLike<T>): Promise<T>;
    static reject(reason?: any): Promise<never>;
    static all<T>(values: Iterable<T | PromiseLike<T>>): Promise<T[]>;
    static race<T>(values: Iterable<T | PromiseLike<T>>): Promise<T>;
    static allSettled<T>(
        values: Iterable<T | PromiseLike<T>>
    ): Promise<Array<{ status: "fulfilled"; value: T } | { status: "rejected"; reason: any }>>;
    static any<T>(values: Iterable<T | PromiseLike<T>>): Promise<T>;
}

// AggregateError used by Promise.any
declare class AggregateError extends Error {
    constructor(errors?: Iterable<any>, message?: string);
    errors: any[];
}