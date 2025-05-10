'use client';

// \) �< ���
// x� �1 | L ���Ќ ��t ĉ �D �<\ \�i��.
export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center my-8">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      <p className="mt-4 text-gray-600">Y� x�| �1X� ����. ��� 0�$�8�...</p>
      <p className="text-sm text-gray-500 mt-2">
        (� 8t� 0| 30~2� � ��   ����)
      </p>
    </div>
  );
}